import DailyIframe, { DailyCall, DailyParticipant } from '@daily-co/daily-js';

export interface VoiceConfig {
  roomUrl: string;
  userName?: string;
}

export class VoiceManager {
  private daily: DailyCall | null = null;
  private localParticipantId: string | null = null;
  private participants: Map<string, DailyParticipant> = new Map();
  private spatialAudioEnabled = true;

  async initialize(config: VoiceConfig): Promise<void> {
    try {
      // Create Daily call object
      this.daily = DailyIframe.createCallObject({
        audioSource: true,
        videoSource: false,
      });

      // Set up event listeners
      this.setupEventListeners();

      // Join room
      await this.daily.join({
        url: config.roomUrl,
        userName: config.userName || 'Player',
      });

      console.log('✅ Voice chat connected');
    } catch (error) {
      console.error('❌ Voice chat failed:', error);
      throw error;
    }
  }

  private setupEventListeners(): void {
    if (!this.daily) return;

    // Track joined participant
    this.daily.on('joined-meeting', (event) => {
      this.localParticipantId = event.participants.local.session_id;
      console.log('🎤 Voice chat joined:', this.localParticipantId);
    });

    // Track participants
    this.daily.on('participant-joined', (event) => {
      if (event.participant) {
        this.participants.set(event.participant.session_id, event.participant);
        console.log('👤 Participant joined voice:', event.participant.user_name);
      }
    });

    this.daily.on('participant-left', (event) => {
      if (event.participant) {
        this.participants.delete(event.participant.session_id);
        console.log('�� Participant left voice:', event.participant.user_name);
      }
    });

    // Handle audio track updates
    this.daily.on('participant-updated', (event) => {
      if (event.participant) {
        this.participants.set(event.participant.session_id, event.participant);
      }
    });
  }

  /**
   * Update spatial audio volumes based on player distances
   * @param playerDistances Map of sessionId -> distance in pixels
   */
  updateSpatialAudio(playerDistances: Map<string, number>): void {
    if (!this.daily || !this.spatialAudioEnabled) return;

    const maxHearingDistance = 500; // pixels

    playerDistances.forEach((distance, sessionId) => {
      if (sessionId === this.localParticipantId) return;

      // Calculate volume: 1.0 at 0 distance, 0.0 at maxHearingDistance
      const volume = Math.max(0, Math.min(1, 1 - (distance / maxHearingDistance)));

      // Set participant volume
      this.daily?.updateParticipant(sessionId, {
        setAudio: volume > 0, // Mute if out of range
      });

      // Update volume (0.0 to 1.0)
      if (volume > 0) {
        this.daily?.setInputDevicesAsync({
          audioSource: true,
        });
      }
    });
  }

  toggleMute(): boolean {
    if (!this.daily) return false;

    const localAudio = this.daily.localAudio();
    this.daily.setLocalAudio(!localAudio);

    return !localAudio;
  }

  toggleSpatialAudio(): boolean {
    this.spatialAudioEnabled = !this.spatialAudioEnabled;

    if (!this.spatialAudioEnabled && this.daily) {
      // Reset all volumes to 1.0 when spatial audio is disabled
      this.participants.forEach((participant, sessionId) => {
        this.daily?.updateParticipant(sessionId, {
          setAudio: true,
        });
      });
    }

    return this.spatialAudioEnabled;
  }

  getParticipantSessionId(userName: string): string | null {
    for (const [sessionId, participant] of this.participants.entries()) {
      if (participant.user_name === userName) {
        return sessionId;
      }
    }
    return null;
  }

  isLocalParticipant(sessionId: string): boolean {
    return sessionId === this.localParticipantId;
  }

  isMuted(): boolean {
    return this.daily ? !this.daily.localAudio() : true;
  }

  async leave(): Promise<void> {
    if (this.daily) {
      await this.daily.leave();
      await this.daily.destroy();
      this.daily = null;
    }
  }

  destroy(): void {
    this.leave();
  }
}
