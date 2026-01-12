import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# RPC URLs
INFURA_URL = os.getenv("INFURA_URL", "")
BSC_RPC = os.getenv("BSC_RPC", "https://bsc-dataseed.binance.org/") # Public RPC default
POLYGON_RPC = os.getenv("POLYGON_RPC", "https://polygon-rpc.com")

SUPPORTED_CHAINS = {
    "ethereum": INFURA_URL,
    "bsc": BSC_RPC,
    "polygon": POLYGON_RPC,
}

POSTGRES_DSN = os.getenv("POSTGRES_DSN", "sqlite:///whales.db")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

ALERT_CHANNELS = [c.strip() for c in os.getenv("ALERT_CHANNELS", "telegram").split(",") if c.strip()]
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))
DEFAULT_ETH_THRESHOLD = Decimal(os.getenv("DEFAULT_ETH_THRESHOLD", "0.001"))
DEFAULT_USDT_THRESHOLD = Decimal(os.getenv("DEFAULT_USDT_THRESHOLD", "100"))
TOKEN_ALERT_THRESHOLD = os.getenv("TOKEN_ALERT_THRESHOLD", "100")

# --- Multi-Chain Token Configuration ---
# العناوين الحقيقية للعملات على كل شبكة
CHAIN_TOKENS = {
    "ethereum": {
        "USDT": ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
        "USDC": ("0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", 6),
        "DAI":  ("0x6B175474E89094C44Da98b954EedeAC495271d0F", 18),
        "WBTC": ("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 8),
    },
    "bsc": {
        # BSC Pegged tokens
        "USDT": ("0x55d398326f99059fF775485246999027B3197955", 18), # Note: BSC USDT is often 18 decimals!
        "USDC": ("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", 18),
        "ETH":  ("0x2170Ed0880ac9A755fd29B2688956BD959F933F8", 18), # Binance-Peg Ethereum
    },
    "polygon": {
        "USDT": ("0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6),
        "USDC": ("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", 6),
        "WETH": ("0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", 18),
    }
}