/**
 * PUMPPORTAL WEBSOCKET
 *
 * Real-time Pump.fun launch detection via PumpPortal WebSocket
 * - FREE data API (no auth required)
 * - Real-time token creation events (1-5 second latency)
 * - Trade activity monitoring
 * - Graduation detection (bonding curve completion)
 */

import { WebSocket } from 'ws';

export interface PumpPortalTokenCreate {
  signature: string;
  mint: string;
  traderPublicKey: string;
  txType: 'create';
  initialBuy: number; // SOL amount
  bondingCurveKey: string;
  vTokensInBondingCurve: number;
  vSolInBondingCurve: number;
  marketCapSol: number;
  name: string;
  symbol: string;
  uri: string; // Metadata URI
  timestamp: number;
}

export interface PumpPortalTrade {
  signature: string;
  mint: string;
  traderPublicKey: string;
  txType: 'buy' | 'sell';
  tokenAmount: number;
  solAmount: number;
  bondingCurveKey: string;
  vTokensInBondingCurve: number;
  vSolInBondingCurve: number;
  marketCapSol: number;
  timestamp: number;
  newTokenBalance?: number;
}

export interface PumpPortalGraduation {
  signature: string;
  mint: string;
  txType: 'graduation';
  raydiumPool: string; // New Raydium pool address
  timestamp: number;
}

type PumpPortalEvent = PumpPortalTokenCreate | PumpPortalTrade | PumpPortalGraduation;

interface SubscriptionMessage {
  method: 'subscribeNewToken' | 'subscribeTokenTrade' | 'subscribeAccountTrade';
  keys?: string[]; // Token mints or wallet addresses
}

class PumpPortalWebSocket {
  private ws: WebSocket | null = null;
  private readonly WS_URL = 'wss://pumpportal.fun/api/data';
  private isConnected = false;
  private reconnectAttempts = 0;
  private readonly MAX_RECONNECT_ATTEMPTS = 10;
  private readonly RECONNECT_DELAY_MS = 5000;

  // Event callbacks
  private onTokenCreateCallback?: (token: PumpPortalTokenCreate) => void;
  private onTradeCallback?: (trade: PumpPortalTrade) => void;
  private onGraduationCallback?: (graduation: PumpPortalGraduation) => void;
  private onErrorCallback?: (error: Error) => void;

  // Token cache to avoid duplicates
  private recentTokens = new Set<string>();
  private readonly CACHE_DURATION_MS = 300000; // 5 minutes

  constructor() {
    console.log('🔌 PumpPortal WebSocket initialized');
  }

  /**
   * Connect to PumpPortal WebSocket
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        console.log('🔌 Connecting to PumpPortal WebSocket...');

        this.ws = new WebSocket(this.WS_URL);

        this.ws.on('open', () => {
          this.isConnected = true;
          this.reconnectAttempts = 0;
          console.log('✅ Connected to PumpPortal WebSocket');
          resolve();
        });

        this.ws.on('message', (data: Buffer) => {
          this.handleMessage(data);
        });

        this.ws.on('error', (error: Error) => {
          console.error('❌ WebSocket error:', error.message);
          if (this.onErrorCallback) {
            this.onErrorCallback(error);
          }
        });

        this.ws.on('close', () => {
          this.isConnected = false;
          console.log('🔌 WebSocket disconnected');
          this.attemptReconnect();
        });

        // Timeout if connection takes too long
        setTimeout(() => {
          if (!this.isConnected) {
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Attempt to reconnect after disconnect
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.MAX_RECONNECT_ATTEMPTS) {
      console.error('❌ Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`🔄 Reconnecting (attempt ${this.reconnectAttempts}/${this.MAX_RECONNECT_ATTEMPTS})...`);

    setTimeout(() => {
      this.connect().catch(err => {
        console.error('Reconnect failed:', err.message);
      });
    }, this.RECONNECT_DELAY_MS);
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(data: Buffer): void {
    try {
      const message: PumpPortalEvent = JSON.parse(data.toString());

      // Handle different event types
      if (message.txType === 'create') {
        this.handleTokenCreate(message as PumpPortalTokenCreate);
      } else if (message.txType === 'buy' || message.txType === 'sell') {
        this.handleTrade(message as PumpPortalTrade);
      } else if (message.txType === 'graduation') {
        this.handleGraduation(message as PumpPortalGraduation);
      }

    } catch (error: any) {
      console.error('Error parsing WebSocket message:', error.message);
    }
  }

  /**
   * Handle token creation event
   */
  private handleTokenCreate(token: PumpPortalTokenCreate): void {
    // Check if we've seen this token recently (avoid duplicates)
    if (this.recentTokens.has(token.mint)) {
      return;
    }

    // Add to cache
    this.recentTokens.add(token.mint);

    // Remove from cache after duration
    setTimeout(() => {
      this.recentTokens.delete(token.mint);
    }, this.CACHE_DURATION_MS);

    // Callback (silently - let the bot decide what to log)
    if (this.onTokenCreateCallback) {
      this.onTokenCreateCallback(token);
    }
  }

  /**
   * Handle trade event
   */
  private handleTrade(trade: PumpPortalTrade): void {
    // Callback
    if (this.onTradeCallback) {
      this.onTradeCallback(trade);
    }
  }

  /**
   * Handle graduation event (bonding curve completed)
   */
  private handleGraduation(graduation: PumpPortalGraduation): void {
    console.log(`\n🎓 GRADUATION: ${graduation.mint.substring(0, 8)}...`);
    console.log(`   Raydium pool: ${graduation.raydiumPool.substring(0, 8)}...`);

    // Callback
    if (this.onGraduationCallback) {
      this.onGraduationCallback(graduation);
    }
  }

  /**
   * Subscribe to new token creations
   */
  subscribeNewTokens(): void {
    if (!this.isConnected || !this.ws) {
      console.error('WebSocket not connected');
      return;
    }

    const message: SubscriptionMessage = {
      method: 'subscribeNewToken'
    };

    this.ws.send(JSON.stringify(message));
    console.log('📡 Subscribed to new token creations');
  }

  /**
   * Subscribe to trades for specific token
   */
  subscribeTokenTrade(mint: string): void {
    if (!this.isConnected || !this.ws) {
      console.error('WebSocket not connected');
      return;
    }

    const message: SubscriptionMessage = {
      method: 'subscribeTokenTrade',
      keys: [mint]
    };

    this.ws.send(JSON.stringify(message));
    console.log(`📡 Subscribed to trades for ${mint.substring(0, 8)}...`);
  }

  /**
   * Subscribe to trades from specific wallet
   */
  subscribeAccountTrade(walletAddress: string): void {
    if (!this.isConnected || !this.ws) {
      console.error('WebSocket not connected');
      return;
    }

    const message: SubscriptionMessage = {
      method: 'subscribeAccountTrade',
      keys: [walletAddress]
    };

    this.ws.send(JSON.stringify(message));
    console.log(`📡 Subscribed to trades from ${walletAddress.substring(0, 8)}...`);
  }

  /**
   * Set callback for token creation events
   */
  onTokenCreate(callback: (token: PumpPortalTokenCreate) => void): void {
    this.onTokenCreateCallback = callback;
  }

  /**
   * Set callback for trade events
   */
  onTrade(callback: (trade: PumpPortalTrade) => void): void {
    this.onTradeCallback = callback;
  }

  /**
   * Set callback for graduation events
   */
  onGraduation(callback: (graduation: PumpPortalGraduation) => void): void {
    this.onGraduationCallback = callback;
  }

  /**
   * Set callback for errors
   */
  onError(callback: (error: Error) => void): void {
    this.onErrorCallback = callback;
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
      console.log('🔌 Disconnected from PumpPortal WebSocket');
    }
  }

  /**
   * Check if connected
   */
  get connected(): boolean {
    return this.isConnected;
  }
}

export { PumpPortalWebSocket };
