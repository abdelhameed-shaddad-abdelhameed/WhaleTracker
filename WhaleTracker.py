from decimal import Decimal
from typing import Optional
from web3 import Web3
from web3.exceptions import Web3Exception
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config

ERC20_BALANCEOF_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]

class TokenService:
    def __init__(self, w3: Web3, address: str, decimals: int):
        self.w3 = w3
        self.decimals = decimals
        self.contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=ERC20_BALANCEOF_ABI)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
    def balance(self, owner: str) -> Optional[Decimal]:
        try:
            raw = self.contract.functions.balanceOf(Web3.to_checksum_address(owner)).call()
            return Decimal(raw) / Decimal(10 ** self.decimals)
        except Exception as e:
            print(f"Token read error: {e}")
            raise e

class BlockchainService:
    def __init__(self, provider_url: str, chain: str = "ethereum"):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.chain = chain
        chain_tokens = config.CHAIN_TOKENS.get(chain, {})
        self.token_services = {
            sym: TokenService(self.w3, addr_data[0], addr_data[1])
            for sym, addr_data in chain_tokens.items()
        }

    def is_connected(self) -> bool:
        try:
            return self.w3.is_connected()
        except Web3Exception:
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
    def get_eth_balance(self, address: str) -> Optional[Decimal]:
        try:
            wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
            return Decimal(self.w3.from_wei(wei, "ether"))
        except Exception as e:
            print(f"ETH read error ({self.chain}): {e}")
            raise e