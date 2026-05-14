import hashlib
import json

def trade_hash(trade: dict) -> str:
    """
    Generate a universal, reproducible SHA-256 hash
    for a trade JSON object.

    This version:
      - Sorts keys alphabetically
      - Removes all extra spaces
      - Does NOT use the \x00 prefix
      - Matches any standard SHA256 generator online
    """
    # Step 1: Canonicalize (stable JSON string)
    canon = json.dumps(trade, separators=(',', ':'), sort_keys=True)
    
    # Step 2: Hash normally (no prefix)
    digest = hashlib.sha256(canon.encode('utf-8')).hexdigest()
    
    return digest


# --- Example usage ---
if __name__ == "__main__":
    trade = {
        "balance":"0.16",
        "commission":"0.00",
        "lot":"0.01",
        "meta":{},
        "price_close":"206.849",
        "price_open":"206.882",
        "profit":"-0.05",
        "side":"sell",
        "stop_loss":"206.851",
        "swap":"0.00",
        "symbol":"gbpjpy",
        "take_profit":"0.000",
        "timestamp_close":"2025-11-28T07:30:09Z",
        "timestamp_open":"2025-11-28T07:20:26Z",
        "trade_id":"49284370",
        "version":"1"
    }

    print(trade_hash(trade))
