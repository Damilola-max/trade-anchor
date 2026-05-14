# canonical_hash.py
import json
import hashlib
from datetime import datetime

# --- Public API --- #

def normalize_trade(raw: dict) -> dict:
    """
    Map incoming raw trade fields to the canonical schema used across FTUK.
    Adjust these mappings to match your source field names if needed.
    Ensure consistent types (strings for decimals/timestamps recommended).
    """
    def fmt_decimal(v, places=3):
        if v is None: return "0"
        if isinstance(v, str): return v
        # convert numeric to fixed-string
        return f"{float(v):.{places}f}"

    def to_iso_z(val):
        if val is None: return ""
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%dT%H:%M:%SZ")
        s = str(val)
        # if input like "2025.11.28 07:20:26" convert common formats optionally
        # Basic normalization: replace space with T and append Z if missing
        if " " in s and "T" not in s:
            s = s.replace(" ", "T")
        if not s.endswith("Z"):
            s = s + "Z"
        return s

    # Map raw keys to canonical keys. Add/remove fields to match your schema.
    canon = {
        "balance": fmt_decimal(raw.get("balance")),
        "commission": fmt_decimal(raw.get("commission")),
        "lot": fmt_decimal(raw.get("lot"), places=2),
        "meta": raw.get("meta", {}),
        "price_close": fmt_decimal(raw.get("priceclose", raw.get("price_close"))),
        "price_open": fmt_decimal(raw.get("priceopen", raw.get("price_open"))),
        "profit": fmt_decimal(raw.get("profit")),
        "side": str(raw.get("type", raw.get("side"))).lower(),
        "stop_loss": fmt_decimal(raw.get("stoploss", raw.get("stop_loss"))),
        "swap": fmt_decimal(raw.get("swap")),
        "symbol": str(raw.get("symbol")).lower(),
        "take_profit": fmt_decimal(raw.get("takeprofit", raw.get("take_profit"))),
        "timestamp_close": to_iso_z(raw.get("timeclose", raw.get("timestamp_close"))),
        "timestamp_open": to_iso_z(raw.get("time", raw.get("timestamp_open"))),
        "trade_id": str(raw.get("ticket", raw.get("trade_id"))),
        "version": "1"
    }
    return canon

def canonical_json(obj: dict) -> str:
    """
    Return compact canonical JSON with keys sorted (recursive).
    This exact string is what you publish in UI (copy button) so users can paste into ANY SHA-256 generator.
    """
    def sort_obj(o):
        if o is None:
            return None
        if isinstance(o, dict):
            return {k: sort_obj(o[k]) for k in sorted(o.keys())}
        if isinstance(o, list):
            return [sort_obj(x) for x in o]
        return o
    sorted_obj = sort_obj(obj)
    return json.dumps(sorted_obj, separators=(',', ':'))

def sha256_hex_of_canonical_obj(obj: dict) -> str:
    canon = canonical_json(obj)
    return hashlib.sha256(canon.encode('utf-8')).hexdigest()

def sha256_hex_of_canonical_json_string(canonical_json_string: str) -> str:
    return hashlib.sha256(canonical_json_string.encode('utf-8')).hexdigest()

# Example quick test (optional)
if __name__ == "__main__":
    raw = {
      "ticket": 49284370,
      "time": "2025-11-28 07:20:26",
      "type": "sell",
      "lot": 0.01,
      "symbol": "gbpjpy",
      "priceopen": 206.882,
      "takeprofit": 0,
      "stoploss": 206.851,
      "timeclose": "2025-11-28 07:30:09",
      "priceclose": 206.849,
      "profit": -0.05,
      "commission": 0,
      "swap": 0,
      "balance": 0.16
    }
    c = normalize_trade(raw)
    cj = canonical_json(c)
    print(cj)
    print(sha256_hex_of_canonical_obj(c))
