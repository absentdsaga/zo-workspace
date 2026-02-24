/**
 * PAPER TRADING CONFIG
 * Used for testing new strategies and validating market conditions.
 * 1:1 identical to mainnet.config.ts except for the flags below.
 */
export const CONFIG = {
  // Mode
  PAPER_TRADE: true,
  MODE_LABEL: 'PAPER',
  USE_JITO: false,               // Set true once you have a Jito API key (JITO_API_KEY env var)

  // Capital
  STARTING_BALANCE: 0.5,          // SOL - paper money, reset freely
  AUTO_REFILL_THRESHOLD: 0.03,    // Add funds when balance hits this
  AUTO_REFILL_AMOUNT: 1.0,        // SOL per refill

  // Position sizing
  MAX_CONCURRENT_POSITIONS: 7,
  MAX_POSITION_SIZE: 0.12,        // 12% of balance per trade
  MIN_BALANCE: 0.05,

  // Entry filters
  MIN_SCORE: 40,
  MIN_SMART_MONEY_CONFIDENCE: 45,
  MIN_SHOCKED_SCORE: 30,

  // Exit thresholds
  TAKE_PROFIT: 1.0,               // +100% activates trailing stop
  STOP_LOSS: -0.30,               // -30% hard stop
  TRAILING_STOP_PERCENT: 0.20,    // 20% drop from peak after TP1
  MAX_HOLD_TIME_MS: 60 * 60 * 1000, // 60 minutes

  // Timing
  SCAN_INTERVAL_MS: 15000,        // 15s between opportunity scans
  MONITOR_INTERVAL_MS: 1000,      // 1s between position checks

  // RPC endpoint - mainnet.helius-rpc.com for reliability
  // ${HELIUS_API_KEY} is replaced at runtime with the actual key
  RPC_URL: 'https://mainnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}',

  // Data files
  TRADES_FILE: '/home/workspace/Projects/survival-agent/data/paper-trades-master.json',
  STATE_FILE: '/home/workspace/Projects/survival-agent/data/paper-trades-state.json',
  BLACKLIST_FILE: '/home/workspace/Projects/survival-agent/data/paper-trades-blacklist.json',
} as const;
