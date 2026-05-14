# cli.py
import os, json, argparse, hashlib
from dotenv import load_dotenv
from anchor_polygon import anchor_trade_hash_hex, anchor_root_hex

load_dotenv()  # ensure .env is read before anchor_polygon import side-effects

def canonical_json(obj: dict) -> str:
    """Recursive key-sort + compact JSON (no spaces)."""
    def sort_obj(o):
        if o is None: return None
        if isinstance(o, dict):
            return {k: sort_obj(o[k]) for k in sorted(o.keys())}
        if isinstance(o, list):
            return [sort_obj(x) for x in o]
        return o
    return json.dumps(sort_obj(obj), separators=(',', ':'))

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def process_single_trade(raw: dict, do_anchor_single: bool):
    """
    Normalize minimal fields -> canonical -> sha256 -> optional per-trade anchor.
    NOTE: If you need strict normalization (types/field names), add it here.
    """
    # Minimal normalization: just ensure strings for keys you care about.
    # If you have a full normalize_trade(), call it here instead.
    canon_str = canonical_json(raw)
    digest = sha256_hex(canon_str)
    tx_trade = None
    if do_anchor_single:
        tx_trade = anchor_trade_hash_hex(digest)
    return {
        "canonical_json": canon_str,
        "sha256": digest,
        "tx_trade": tx_trade
    }

def build_merkle_root(leaves_hex):
    """
    Simple binary Merkle using SHA256 with domain tag for internal nodes.
    Internal node: H(0x01 || left || right); leaves are raw sha256 hex strings (32 bytes).
    Returns: root hex (64 chars).
    """
    import binascii, hashlib
    nodes = [bytes.fromhex(h) for h in leaves_hex]
    if not nodes:
        return None
    while len(nodes) > 1:
        nxt = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i+1] if i+1 < len(nodes) else nodes[i]  # duplicate last if odd
            nxt.append(hashlib.sha256(b"\x01" + left + right).digest())
        nodes = nxt
    return nodes[0].hex()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="single trade JSON string")
    ap.add_argument("--file", help="path to JSON file [list of trades] or TSV")
    ap.add_argument("--anchor", action="store_true", help="perform on-chain anchoring")
    ap.add_argument("--anchor-single", action="store_true", help="anchor each trade hash visibly")
    ap.add_argument("--anchor-batch", action="store_true", help="also anchor Merkle root for all trades")
    args = ap.parse_args()

    trades = []
    if args.json:
        trades.append(json.loads(args.json))
    elif args.file:
        if args.file.lower().endswith(".json"):
            trades = json.load(open(args.file))
        else:
            # naive TSV parser; adjust columns per your layout
            with open(args.file, "r") as f:
                for ln in f:
                    parts = ln.rstrip("\n").split("\t")
                    if len(parts) < 2: continue
                    # map whatever columns you have to a dict
                    # Example order used earlier:
                    raw = {
                        "ticket": parts[0] if len(parts) > 0 else None,
                        "time": parts[1] if len(parts) > 1 else None,
                        "type": parts[2] if len(parts) > 2 else None,
                        "lot": parts[3] if len(parts) > 3 else None,
                        "symbol": parts[4] if len(parts) > 4 else None,
                        "priceopen": parts[5] if len(parts) > 5 else None,
                        "takeprofit": parts[6] if len(parts) > 6 else None,
                        "stoploss": parts[7] if len(parts) > 7 else None,
                        "timeclose": parts[8] if len(parts) > 8 else None,
                        "priceclose": parts[9] if len(parts) > 9 else None,
                        "profit": parts[10] if len(parts) > 10 else None,
                        "commission": parts[11] if len(parts) > 11 else None,
                        "swap": parts[12] if len(parts) > 12 else None,
                        "balance": parts[13] if len(parts) > 13 else None
                    }
                    trades.append(raw)
    else:
        print("Provide --json or --file")
        return

    # Per-trade: canonicalize, hash, (optional) anchor individual
    results = []
    for t in trades:
        res = process_single_trade(t, do_anchor_single=(args.anchor and args.anchor_single))
        print("\n=== TRADE ===")
        print("Canonical:", res["canonical_json"])
        print("SHA-256  :", res["sha256"])
        if res["tx_trade"]:
            print("Tx (single):", res["tx_trade"])
        results.append(res)

    # Optional batch merkle
    batch_tx = None
    root_hex = None
    if args.anchor and args.anchor_batch and results:
        leaves = [r["sha256"] for r in results]
        root_hex = build_merkle_root(leaves)
        print("\nMerkle root:", root_hex)
        batch_tx = anchor_root_hex(root_hex)
        print("Tx (batch):", batch_tx)

    # Write artifact
    os.makedirs("out", exist_ok=True)
    with open("out/anchor_result.json", "w") as f:
        json.dump({
            "items": results,
            "batch_root": root_hex,
            "tx_batch": batch_tx
        }, f, indent=2)
    print("\nWrote out/anchor_result.json")

if __name__ == "__main__":
    main()
