import DailyIframe from '@daily-co/daily-js';

interface PlayerPosition {
  playerId: string;
  x: number;
  y: number;
  elevation: number;
}

export class VoiceManager {
  private daily: any = null;
  private localPlayerId: string = '';
  private audioNodes: Map<string, {
    source: MediaStreamAudioSourceNode;
    gain: GainNode;
    panner: StereoPannerNode;
  }> = new Map();
  private audioContext: AudioContext;
  private maxHearingDistance: number = 500; // Pixels

  constructor() {
    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  }

  async createRoom(roomUrl?: string): Promise<void> {
    // Create Daily call object
    this.daily = DailyIframe.createCallObject({
      audioSource: true,
      videoSource: false, // Voice only for now
    });

    // Listen for participant events
    this.daily
      .on('joined-meeting', this.onJoined.bind(this))
      .on('participant-joined', this.onParticipantJoined.bind(this))
      .on('participant-left', this.onParticipantLeft.bind(this))
      .on('track-started', this.onTrackStarted.bind(this))
      .on('track-stopped', this.onTrackStopped.bind(this));

    // Join the room
    const targetUrl = roomUrl || 'https://ourroom.daily.co/spatial-worlds';
    console.log('🎤 Joining voice room:', targetUrl);

    try {
      await this.daily.join({ url: targetUrl });
    } catch (error) {
      console.error('❌ Failed to join voice room:', error);
      throw error;
    }
  }

  private onJoined(event: any) {
    console.log('🎤 Joined voice room:', event);
    this.localPlayerId = event.participants.local.session_id;
  }

  private onParticipantJoined(event: any) {
    console.log('👤 Participant joined:', event.participant.user_name);
  }

  private onParticipantLeft(event: any) {
    console.log('👤 Participant left:', event.participant.user_name);
    const sessionId = event.participant.session_id;

    // Clean up audio nodes
    const nodes = this.audioNodes.get(sessionId);
    if (nodes) {
      nodes.source.disconnect();
      nodes.gain.disconnect();
      nodes.panner.disconnect();
      this.audioNodes.delete(sessionId);
    }
  }

  private onTrackStarted(event: any) {
    const { participant, track } = event;

    // Ignore local tracks and non-audio tracks
    if (participant.local || track.kind !== 'audio') return;

    console.log('🎵 Audio track started:', participant.user_name);

    // Create Web Audio API nodes for spatial audio
    const stream = new MediaStream([track]);
    const source = this.audioContext.createMediaStreamSource(stream);
    const gain = this.audioContext.createGain();
    const panner = this.audioContext.createStereoPanner();

    // Connect: source → gain → panner → destination
    source.connect(gain);
    gain.connect(panner);
    panner.connect(this.audioContext.destination);

    // Start with zero volume (will be updated based on distance)
    gain.gain.value = 0;
    panner.pan.value = 0;

    // Store the nodes
    this.audioNodes.set(participant.session_id, { source, gain, panner });
  }

  private onTrackStopped(event: any) {
    const { participant } = event;
    console.log('🎵 Audio track stopped:', participant.user_name);

    // Disconnect and remove nodes
    const nodes = this.audioNodes.get(participant.session_id);
    if (nodes) {
      nodes.source.disconnect();
      nodes.gain.disconnect();
      nodes.panner.disconnect();
      this.audioNodes.delete(participant.session_id);
    }
  }

  updateSpatialAudio(localPos: PlayerPosition, remotePlayers: PlayerPosition[]) {
    remotePlayers.forEach(remote => {
      const nodes = this.audioNodes.get(remote.playerId);
      if (!nodes) return;

      // Calculate distance
      const dx = remote.x - localPos.x;
      const dy = remote.y - localPos.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      // Calculate elevation difference
      const elevationDiff = Math.abs(remote.elevation - localPos.elevation);

      // Volume based on distance
      let volume = Math.max(0, 1 - (distance / this.maxHearingDistance));

      // Elevation attenuation (each level reduces volume by 50%)
      const elevationMultiplier = Math.pow(0.5, elevationDiff);
      volume *= elevationMultiplier;

      // Apply volume
      nodes.gain.gain.value = volume;

      // Stereo panning based on x-axis position
      const pan = Math.max(-1, Math.min(1, dx / this.maxHearingDistance));
      nodes.panner.pan.value = pan;
    });
  }

  async leave() {
    if (this.daily) {
      await this.daily.leave();
      this.daily.destroy();
      this.daily = null;
    }

    // Clean up audio nodes
    this.audioNodes.forEach(nodes => {
      nodes.source.disconnect();
      nodes.gain.disconnect();
      nodes.panner.disconnect();
    });
    this.audioNodes.clear();
  }

  setMaxHearingDistance(distance: number) {
    this.maxHearingDistance = distance;
  }

  getLocalPlayerId(): string | null {
    return this.localPlayerId;
  }
}
