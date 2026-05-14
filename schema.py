from decimal import Decimal, ROUND_HALF_UP, getcontext
from dateutil import parser as dtparser
import pytz

# Set decimal context for deterministic rounding
getcontext().prec = 28  # high precision
SCALE = {
    "lot": 2,            # 0.01
    "price": 3,          # 206.882
    "profit": 2,         # -0.05
    "money": 2,          # 0.16
}

def q(value: str | float | int, places: int) -> str:
    d = Decimal(str(value))
    fmt = Decimal(1).scaleb(-places)  # e.g., 10^-3 for 3 dp
    return str(d.quantize(fmt, rounding=ROUND_HALF_UP))

def to_utc_iso8601(s: str) -> str:
    # Accepts "YYYY.MM.DD HH:MM:SS" or "YYYY-MM-DD HH:MM:SS" etc.
    dt = dtparser.parse(s)
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(pytz.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def normalize_trade_dict(raw: dict) -> dict:
    """
    Enforce a strict schema and deterministic string encodings.
    REQUIRED KEYS (case-insensitive acceptable on input):
      ticket, time, type, lot, symbol, priceopen, takeprofit, stoploss,
      timeclose, priceclose, profit, commission, swap, balance
    """
    # Canonical field names (fixed order used later during canonicalization)
    ticket      = int(raw["ticket"])
    time        = to_utc_iso8601(str(raw["time"]).replace(".", "-"))
    side        = str(raw["type"]).lower().strip()  # "buy" or "sell"
    lot         = q(raw["lot"], SCALE["lot"])
    symbol      = str(raw["symbol"]).lower().strip()

    priceopen   = q(raw["priceopen"], SCALE["price"])
    takeprofit  = q(raw["takeprofit"], SCALE["price"])
    stoploss    = q(raw["stoploss"], SCALE["price"])

    timeclose   = to_utc_iso8601(str(raw["timeclose"]).replace(".", "-"))
    priceclose  = q(raw["priceclose"], SCALE["price"])

    profit      = q(raw["profit"], SCALE["profit"])
    commission  = q(raw["commission"], SCALE["money"])
    swap        = q(raw["swap"], SCALE["money"])
    balance     = q(raw["balance"], SCALE["money"])

    # Canonical payload (ordered later by canonicaljson)
    return {
        "version": "1",
        "trade_id": str(ticket),
        "timestamp_open": time,
        "timestamp_close": timeclose,
        "symbol": symbol,
        "side": side,                    # "buy" | "sell"
        "lot": lot,                      # stringified decimals
        "price_open": priceopen,
        "price_close": priceclose,
        "take_profit": takeprofit,
        "stop_loss": stoploss,
        "profit": profit,
        "commission": commission,
        "swap": swap,
        "balance": balance,
        "meta": {},                      # reserved for future extensions
    }

def parse_tsv_line(line: str) -> dict:
    """
    Accepts a single MT4/MT5-like TSV line:
    ticket\ttime\ttype\tlot\tsymbol\tpriceopen\ttakeprofit\tstoploss\ttimeclose\tpriceclose\tprofit\tcommission\tswap\tbalance
    Example:
    49284370\t2025.11.28 07:20:26\tsell\t0.01\tgbpjpy\t206.882\t0.000\t206.851\t2025.11.28 07:30:09\t206.849\t-0.05\t0.00\t0.00\t0.16
    """
    parts = [p.strip() for p in line.strip().split("\t")]
    if len(parts) != 14:
        raise ValueError("TSV line does not have 14 fields")

    return {
        "ticket": parts[0],
        "time": parts[1].replace(".", "-"),
        "type": parts[2],
        "lot": parts[3],
        "symbol": parts[4],
        "priceopen": parts[5],
        "takeprofit": parts[6],
        "stoploss": parts[7],
        "timeclose": parts[8].replace(".", "-"),
        "priceclose": parts[9],
        "profit": parts[10],
        "commission": parts[11],
        "swap": parts[12],
        "balance": parts[13],
    }
