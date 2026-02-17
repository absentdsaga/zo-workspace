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

  // Capital - matches paper exactly
  STARTING_BALANCE: 0.5,
  AUTO_REFILL_THRESHOLD: 0.03,
  AUTO_REFILL_AMOUNT: 1.0,

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
  MONITOR_INTERVAL_MS: 5000,

  // Data files - separate from paper so both can run simultaneously
  TRADES_FILE: '/tmp/mainnet-trades-master.json',
  STATE_FILE: '/tmp/mainnet-trades-state.json',
  BLACKLIST_FILE: '/tmp/mainnet-trades-blacklist.json',
} as const;
