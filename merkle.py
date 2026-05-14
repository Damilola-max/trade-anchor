from typing import List, Tuple
from canonicalise import node_hash

def build_merkle_root(leaves: List[bytes]) -> bytes:
    if not leaves:
        import hashlib
        return hashlib.sha256(b"").digest()
    level = leaves[:]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])  # duplicate last for odd count
        level = [node_hash(level[i], level[i+1]) for i in range(0, len(level), 2)]
    return level[0]

def merkle_proof(leaves: List[bytes], index: int) -> Tuple[bytes, list[bytes]]:
    """
    Returns (root, proof) where proof is list of sibling nodes (bytes)
    """
    if index < 0 or index >= len(leaves):
        raise IndexError("index out of range")
    level = leaves[:]
    idx = index
    proof = []
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        sibling_idx = idx + 1 if idx % 2 == 0 else idx - 1
        proof.append(level[sibling_idx])
        # build next level
        next_level = []
        for i in range(0, len(level), 2):
            next_level.append(node_hash(level[i], level[i+1]))
        level = next_level
        idx //= 2
    root = level[0]
    return root, proof

def verify_proof(leaf: bytes, index: int, proof: list[bytes], expected_root: bytes) -> bool:
    from canonicalise import node_hash
    h = leaf
    idx = index
    for sib in proof:
        if idx % 2 == 0:
            h = node_hash(h, sib)
        else:
            h = node_hash(sib, h)
        idx //= 2
    return h == expected_root
