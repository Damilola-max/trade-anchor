import hashlib
import canonicaljson

DOMAIN_LEAF = b"\x00"
DOMAIN_NODE = b"\x01"

def canonical_bytes(payload: dict) -> bytes:
    # Deterministic encoding with canonicaljson (RFC8785-like)
    return canonicaljson.encode_canonical_json(payload)

def leaf_digest(canonical: bytes) -> bytes:
    return hashlib.sha256(DOMAIN_LEAF + canonical).digest()

def leaf_hex(canonical: bytes) -> str:
    return hashlib.sha256(DOMAIN_LEAF + canonical).hexdigest()

def node_hash(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(DOMAIN_NODE + left + right).digest()
