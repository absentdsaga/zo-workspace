/**
 * MAINNET TRADING CONFIG
 * Real money. Conservative settings until track record is established.
 * DO NOT change these without paper testing the change first.
 *
 * To test a setting change:
 *   1. Change it in paper.config.ts
 *   2. Run paper bot for 48h+
 *   3. If win rate stays ≥30% and net P&L is positive, apply here
 */
export const CONFIG = {
  // Mode
  PAPER_TRADE: false,
  MODE_LABEL: 'MAINNET',
  USE_JITO: false,               // Set true once you have a Jito API key (JITO_API_KEY env var)

  // Capital - matches paper exactly
  STARTING_BALANCE: 0.5,
  AUTO_REFILL_THRESHOLD: 0,       // Disabled on mainnet - no fake refills with real money
  AUTO_REFILL_AMOUNT: 0,          // Disabled on mainnet

  // Position sizing - matches paper exactly
  MAX_CONCURRENT_POSITIONS: 7,
  MAX_POSITION_SIZE: 0.12,        // 12% of balance per trade
  MIN_BALANCE: 0.05,

  // Entry filters - matches paper exactly
  MIN_SCORE: 40,
  MIN_SMART_MONEY_CONFIDENCE: 45,
  MIN_SHOCKED_SCORE: 30,

  // Exit thresholds - matches paper exactly
  TAKE_PROFIT: 1.0,
  STOP_LOSS: -0.30,               // -30% hard stop
  TRAILING_STOP_PERCENT: 0.20,    // 20% drop from peak after TP1
  MAX_HOLD_TIME_MS: 60 * 60 * 1000, // 60 minutes

  // Timing - matches paper exactly
  SCAN_INTERVAL_MS: 15000,
  MONITOR_INTERVAL_MS: 1000,

  // RPC endpoint - mainnet.helius-rpc.com for reliability
  // ${HELIUS_API_KEY} is replaced at runtime with the actual key
  RPC_URL: 'https://mainnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}',

  // Data files - persistent storage (survives restarts)
  TRADES_FILE: '/home/workspace/Projects/survival-agent/data/mainnet-trades-master.json',
  STATE_FILE: '/home/workspace/Projects/survival-agent/data/mainnet-trades-state.json',
  BLACKLIST_FILE: '/home/workspace/Projects/survival-agent/data/mainnet-trades-blacklist.json',
} as const;
