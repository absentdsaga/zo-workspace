import DailyIframe from '@daily-co/daily-js';

interface PlayerPosition {
  playerId: string;
  x: number;
  y: number;
  elevation: number;
}

interface ParticipantAudio {
  source: MediaStreamAudioSourceNode;
  gain: GainNode;
  panner: StereoPannerNode;
  compressor: DynamicsCompressorNode;
}

export class VoiceManager {
  private daily: any = null;
  private localPlayerId: string = '';
  private audioContext: AudioContext | null = null;
  private audioNodes: Map<string, ParticipantAudio> = new Map();
  private maxHearingDistance: number = 500;
  private joined = false;
  private roomUrl: string;
  private pendingTracks: Array<{ participant: any; track: MediaStreamTrack }> = [];
  private participantCount = 0;

  constructor() {
    this.roomUrl = 'https://ourroom.daily.co/spatial-worlds';
  }

  async createRoom(): Promise<void> {
    this.setupAutoplayResume();

    this.daily = DailyIframe.createCallObject({
      audioSource: true,
      videoSource: false,
    });

    this.daily
      .on('joined-meeting', this.onJoined.bind(this))
      .on('participant-joined', this.onParticipantJoined.bind(this))
      .on('participant-left', this.onParticipantLeft.bind(this))
      .on('track-started', this.onTrackStarted.bind(this))
      .on('track-stopped', this.onTrackStopped.bind(this))
      .on('error', (e: any) => console.warn('Daily error:', e));

    console.log('🎤 Joining voice room:', this.roomUrl);
    await this.daily.join({ url: this.roomUrl });
  }

  private setupAutoplayResume() {
    const createContext = () => {
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        console.log('🔊 AudioContext created, state:', this.audioContext.state);
      }
      if (this.audioContext.state === 'suspended') {
        this.audioContext.resume().then(() => {
          console.log('🔊 AudioContext resumed');
        });
      }
      // Process any tracks that arrived before user gesture
      this.processPendingTracks();
    };

    const events = ['click', 'keydown', 'touchstart'];
    const handler = () => {
      createContext();
      events.forEach(e => document.removeEventListener(e, handler));
    };
    events.forEach(e => document.addEventListener(e, handler, { once: false }));
  }

  private ensureAudioContext(): AudioContext | null {
    if (!this.audioContext) return null;
    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }
    return this.audioContext;
  }

  private processPendingTracks() {
    const pending = [...this.pendingTracks];
    this.pendingTracks = [];
    for (const { participant, track } of pending) {
      this.setupTrackAudio(participant, track);
    }
  }

  private onJoined(event: any) {
    this.localPlayerId = event.participants.local.session_id;
    this.joined = true;
    console.log('🎤 Joined voice room, local ID:', this.localPlayerId);

    // Count existing participants
    const participants = this.daily?.participants();
    if (participants) {
      const remoteCount = Object.keys(participants).filter(k => k !== 'local').length;
      this.participantCount = remoteCount;
      console.log(`🎤 ${remoteCount} other participant(s) already in room`);
    }
  }

  private onParticipantJoined(event: any) {
    const p = event.participant;
    if (p.local) return;
    this.participantCount++;
    console.log(`👤 Voice participant joined: ${p.session_id} (${this.participantCount} total)`);
  }

  private onParticipantLeft(event: any) {
    const sessionId = event.participant?.session_id;
    if (!sessionId) return;
    this.participantCount = Math.max(0, this.participantCount - 1);
    console.log(`👤 Voice participant left: ${sessionId} (${this.participantCount} total)`);
    this.removeParticipantAudio(sessionId);
  }

  private onTrackStarted(event: any) {
    const { participant, track } = event;
    if (!participant || participant.local || track.kind !== 'audio') return;

    const ctx = this.ensureAudioContext();
    if (!ctx) {
      console.warn('🔊 AudioContext not ready — queuing track for', participant.session_id);
      this.pendingTracks.push({ participant, track });
      return;
    }

    this.setupTrackAudio(participant, track);
  }

  private setupTrackAudio(participant: any, track: MediaStreamTrack) {
    const ctx = this.ensureAudioContext();
    if (!ctx) return;

    // Remove old nodes if re-subscribing
    this.removeParticipantAudio(participant.session_id);

    console.log('🎵 Setting up spatial audio for:', participant.session_id);

    const stream = new MediaStream([track]);
    const source = ctx.createMediaStreamSource(stream);
    const gain = ctx.createGain();
    const panner = ctx.createStereoPanner();
    const compressor = ctx.createDynamicsCompressor();

    compressor.threshold.value = -24;
    compressor.knee.value = 30;
    compressor.ratio.value = 12;

    source.connect(gain);
    gain.connect(panner);
    panner.connect(compressor);
    compressor.connect(ctx.destination);

    // Start at full volume — spatial audio will adjust based on distance
    gain.gain.value = 1.0;
    panner.pan.value = 0;

    this.audioNodes.set(participant.session_id, { source, gain, panner, compressor });
  }

  private onTrackStopped(event: any) {
    const sessionId = event.participant?.session_id;
    if (sessionId) this.removeParticipantAudio(sessionId);
  }

  private removeParticipantAudio(sessionId: string) {
    const nodes = this.audioNodes.get(sessionId);
    if (!nodes) return;
    try {
      nodes.source.disconnect();
      nodes.gain.disconnect();
      nodes.panner.disconnect();
      nodes.compressor.disconnect();
    } catch {}
    this.audioNodes.delete(sessionId);
  }

  updateSpatialAudio(localPos: PlayerPosition, remotePlayers: PlayerPosition[]) {
    if (!this.joined) return;

    remotePlayers.forEach(remote => {
      const nodes = this.audioNodes.get(remote.playerId);
      if (!nodes) return;

      const dx = remote.x - localPos.x;
      const dy = remote.y - localPos.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const elevationDiff = Math.abs(remote.elevation - localPos.elevation);

      const rolloff = 2;
      let volume = 1 / (1 + rolloff * (distance / this.maxHearingDistance));
      if (distance > this.maxHearingDistance) volume = 0;
      volume *= Math.pow(0.5, elevationDiff);

      const now = this.audioContext?.currentTime ?? 0;
      nodes.gain.gain.linearRampToValueAtTime(volume, now + 0.1);

      const angle = Math.atan2(dy, dx);
      nodes.panner.pan.linearRampToValueAtTime(
        Math.max(-1, Math.min(1, Math.sin(angle))),
        now + 0.1
      );
    });
  }

  async leave() {
    if (this.daily) {
      try {
        await this.daily.leave();
        this.daily.destroy();
      } catch {}
      this.daily = null;
    }

    this.audioNodes.forEach((nodes) => {
      try {
        nodes.source.disconnect();
        nodes.gain.disconnect();
        nodes.panner.disconnect();
        nodes.compressor.disconnect();
      } catch {}
    });
    this.audioNodes.clear();

    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
    this.audioContext = null;
    this.joined = false;
  }

  setMaxHearingDistance(distance: number) {
    this.maxHearingDistance = distance;
  }

  getLocalPlayerId(): string | null {
    return this.localPlayerId || null;
  }

  isJoined(): boolean {
    return this.joined;
  }

  getParticipantCount(): number {
    return this.participantCount;
  }

  getAudioNodeCount(): number {
    return this.audioNodes.size;
  }
}
