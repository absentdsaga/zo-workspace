"""
Polymarket Trading Bot Configuration
Top 0.01% Strategy Configuration
"""

# Trading parameters
MIN_PROFIT_THRESHOLD = 0.003  # 0.3% minimum profit after fees (OPTIMIZED for more opportunities)
MAX_POSITION_SIZE = 50  # Max $50 per trade (half our bankroll for safety)
MIN_LIQUIDITY = 5000  # Minimum market liquidity to avoid slippage
MAX_CONCURRENT_TRADES = 3  # Maximum number of simultaneous positions

# Strategy weights (sum to 1.0)
STRATEGY_WEIGHTS = {
    'sum_to_one_arb': 0.50,  # Highest weight - most reliable
    'cross_market_arb': 0.25,  # Second priority
    'momentum_scalp': 0.15,  # Fast markets (crypto 15min, sports)
    'market_making': 0.10,  # Passive income
}

# Market selection criteria
PREFERRED_MARKETS = {
    'crypto': {
        'min_volume': 10000,
        'max_spread': 0.03,  # 3% max spread
        'update_frequency': '15min',  # 15-minute markets for speed
    },
    'sports': {
        'min_volume': 50000,
        'max_spread': 0.02,
        'time_to_resolution': 86400,  # Within 24 hours
    },
    'politics': {
        'min_volume': 100000,
        'max_spread': 0.02,
        'avoid_long_term': True,  # Skip markets > 30 days out
    }
}

# Risk management
STOP_LOSS_PERCENT = 0.15  # Stop trading if down 15% of bankroll
TAKE_PROFIT_TARGET = 2.0  # 2x initial capital = success
DAILY_LOSS_LIMIT = 0.10  # Max 10% loss per day
WINNING_STREAK_SCALING = 1.2  # Increase position size by 20% after 3 wins

# Execution settings
ORDER_TIMEOUT = 30  # seconds
MAX_SLIPPAGE = 0.01  # 1% max slippage tolerance
USE_MAKER_ORDERS = True  # Avoid taker fees when possible
CANCEL_UNFILLED_AFTER = 60  # Cancel orders after 60 seconds if not filled

# API endpoints
POLYMARKET_API = "https://clob.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
STRAPI_API = "https://strapi-matic.poly.market"

# Update intervals
MARKET_SCAN_INTERVAL = 5  # Scan for opportunities every 5 seconds
POSITION_CHECK_INTERVAL = 10  # Check positions every 10 seconds
ORDERBOOK_UPDATE_INTERVAL = 2  # Update orderbook data every 2 seconds

# Fee structure (Polymarket)
TAKER_FEE = 0.0  # No taker fee currently
MAKER_FEE = 0.0  # No maker fee
GAS_ESTIMATE = 0.001  # Est $0.001 gas per transaction on Polygon

# Advanced features
ENABLE_WEBSOCKET = True  # Real-time market data
ENABLE_MULTI_ACCOUNT = False  # For scaling beyond single account limits
ENABLE_SMART_ROUTING = True  # Route to best price across markets
ENABLE_POSITION_HEDGING = True  # Auto-hedge large positions

# Logging and monitoring
LOG_LEVEL = "INFO"
LOG_FILE = "polymarket_bot.log"
ENABLE_TELEGRAM_ALERTS = False  # Set to True to get trade alerts
ENABLE_METRICS_TRACKING = True  # Track all metrics for analysis
