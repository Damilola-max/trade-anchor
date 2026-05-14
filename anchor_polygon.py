# anchor_polygon.py
import os
from web3 import Web3
from hexbytes import HexBytes
from dotenv import load_dotenv

# Load .env from project root automatically
load_dotenv()

def _require(name: str) -> str:
    v = os.getenv(name)
    if not v or not v.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v.strip()

POLYGON_RPC_URL = _require("POLYGON_RPC_URL")
ANCHOR_FROM_ADDRESS = _require("ANCHOR_FROM_ADDRESS")
ANCHOR_PRIVATE_KEY = _require("ANCHOR_PRIVATE_KEY")
ANCHOR_TO_ADDRESS = os.getenv(
    "ANCHOR_TO_ADDRESS", "0x0000000000000000000000000000000000000000"
).strip()

# Connect to Polygon RPC
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
if not w3.is_connected():
    raise RuntimeError(
        "Cannot connect to Polygon RPC. Check POLYGON_RPC_URL, key validity, or network."
    )

def _checksum(addr: str) -> str:
    try:
        return Web3.to_checksum_address(addr)
    except Exception:
        raise RuntimeError(f"Invalid address (must be checksum): {addr}")

FROM = _checksum(ANCHOR_FROM_ADDRESS)
TO = _checksum(ANCHOR_TO_ADDRESS)

def anchor_trade_hash_hex(trade_hash_hex: str) -> str:
    """
    Anchor a single trade hash directly. The hash will be visible in Polygonscan Input Data.
    Args:
        trade_hash_hex: 64 hex chars (no 0x prefix). If '0x' provided, it's stripped.
    Returns:
        tx hash hex string (0x...)
    """
    if trade_hash_hex.startswith("0x"):
        trade_hash_hex = trade_hash_hex[2:]
    if len(trade_hash_hex) != 64 or any(
        c not in "0123456789abcdefABCDEF" for c in trade_hash_hex
    ):
        raise RuntimeError("trade_hash_hex must be 64 hex chars (sha256 digest).")

    nonce = w3.eth.get_transaction_count(FROM)

    # Include chainId=137 → Polygon mainnet
    tx = {
        "nonce": nonce,
        "to": TO,
        "value": 0,
        "data": "0x" + trade_hash_hex,
        "chainId": 137,
    }

    # Gas configuration
    try:
        tx["gas"] = w3.eth.estimate_gas(tx)
    except Exception:
        tx["gas"] = 100000

    try:
        tx["gasPrice"] = w3.eth.gas_price
    except Exception:
        tx["gasPrice"] = w3.to_wei("40", "gwei")

    # Sign and send
    signed = w3.eth.account.sign_transaction(tx, private_key=ANCHOR_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return w3.to_hex(tx_hash)

def anchor_root_hex(root_hex: str) -> str:
    """Batch compatibility: anchor a Merkle root by reusing the same path."""
    if root_hex.startswith("0x"):
        root_hex = root_hex[2:]
    return anchor_trade_hash_hex(root_hex)

# Quick connectivity self-test (optional)
if __name__ == "__main__":
    print("RPC ok:", w3.is_connected())
    print("From:", FROM)
    print("To  :", TO)
