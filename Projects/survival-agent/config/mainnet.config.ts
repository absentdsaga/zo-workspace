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

  // Capital - conservative until proven profitable on mainnet
  STARTING_BALANCE: 0.1,          // SOL - real money, start small
  AUTO_REFILL_THRESHOLD: 0,       // No auto-refill on mainnet
  AUTO_REFILL_AMOUNT: 0,

  // Position sizing - tighter than paper
  MAX_CONCURRENT_POSITIONS: 3,    // Max 3 positions at once (vs 7 paper)
  MAX_POSITION_SIZE: 0.05,        // 5% of balance per trade (vs 12% paper)
  MIN_BALANCE: 0.02,

  // Entry filters - same as paper (don't loosen these)
  MIN_SCORE: 40,
  MIN_SMART_MONEY_CONFIDENCE: 45,
  MIN_SHOCKED_SCORE: 30,

  // Exit thresholds - tighter stop loss than paper
  TAKE_PROFIT: 1.0,               // +100% activates trailing stop
  STOP_LOSS: -0.20,               // -20% hard stop (vs -30% paper)
  TRAILING_STOP_PERCENT: 0.20,    // 20% drop from peak after TP1
  MAX_HOLD_TIME_MS: 60 * 60 * 1000, // 60 minutes

  // Timing - same as paper
  SCAN_INTERVAL_MS: 15000,
  MONITOR_INTERVAL_MS: 5000,

  // Data files - separate from paper so both can run simultaneously
  TRADES_FILE: '/tmp/mainnet-trades-master.json',
  STATE_FILE: '/tmp/mainnet-trades-state.json',
  BLACKLIST_FILE: '/tmp/mainnet-trades-blacklist.json',
} as const;
