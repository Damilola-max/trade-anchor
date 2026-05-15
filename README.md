# Trade-Anchor

Blockchain-based machine learning prediction anchoring system using Polygon smart contracts and Merkle tree verification.

## Overview

Trade-Anchor provides immutable, timestamped proof of ML predictions by anchoring cryptographic hashes to the Polygon blockchain. This enables:

- **Prediction provenance**: Cryptographic proof that a specific prediction existed at a specific time
- **Tamper-evident records**: Any modification to historical predictions becomes detectable
- **Audit trails**: Complete history of model outputs for compliance and verification
- **Batch anchoring**: Efficient Merkle tree-based anchoring of multiple predictions in a single transaction

## Architecture

```
Raw Trade Data
    ↓
Normalization & Canonicalization
    ↓
SHA-256 Hashing
    ↓
├── Single Trade Anchoring (per-trade)
└── Batch Merkle Root Anchoring (bulk)
    ↓
Polygon Blockchain Transaction
```

## Key Components

| Module | Purpose |
|--------|---------|
| `anchor_polygon.py` | Polygon blockchain integration and transaction handling |
| `cli.py` | Command-line interface for trade processing and anchoring |
| `merkle.py` | Merkle tree construction and verification |
| `canonical_hash.py` | Canonical JSON normalization for deterministic hashing |
| `schema.py` | Data validation schemas |
| `trade_hash.py` | Trade-specific hashing utilities |
| `ipfs_client.py` | Optional IPFS integration for off-chain storage |

## Installation

```bash
# Clone the repository
git clone https://github.com/Damilola-max/trade-anchor.git
cd trade-anchor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
# Polygon RPC endpoint (e.g., from Alchemy, Infura, or QuickNode)
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Wallet address that will sign and send anchor transactions
ANCHOR_FROM_ADDRESS=0xYourWalletAddress

# Private key for signing (keep secure!)
ANCHOR_PRIVATE_KEY=0xYourPrivateKey

# Optional: destination address for anchor transactions (default: zero address)
ANCHOR_TO_ADDRESS=0x0000000000000000000000000000000000000000
```

## Usage

### Single Trade Anchoring

```bash
python cli.py --input trade.json --anchor-single
```

### Batch Anchoring with Merkle Tree

```bash
python cli.py --input trades.json --merkle --anchor-merkle
```

### Verify Anchored Hash

```python
from anchor_polygon import verify_anchor

# Verify a previously anchored hash on-chain
is_valid = verify_anchor(transaction_hash, expected_data_hash)
```

## How It Works

### 1. Canonicalization

Before hashing, all trade data is normalized to ensure deterministic output:

```python
{
  "symbol": "BTCUSD",
  "price": 50000.00,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Becomes canonical JSON (sorted keys, no whitespace):

```json
{"price":50000.0,"symbol":"BTCUSD","timestamp":"2024-01-15T10:30:00Z"}
```

### 2. Hashing

SHA-256 produces a 64-character hex digest:

```
a3f5c8...b2e1d9  (truncated for display)
```

### 3. Blockchain Anchoring

The hash is embedded in a Polygon transaction, creating an immutable timestamp:

- **Transaction hash**: `0x1a2b3c...4d5e6f`
- **Block number**: 52,341,567
- **Timestamp**: 2024-01-15 10:31:22 UTC

### 4. Merkle Trees for Batching

Multiple trades are combined into a Merkle tree:

```
         Root Hash (anchored once)
        /                      \
   Hash A                      Hash B
  /       \                  /       \
Trade1   Trade2          Trade3   Trade4
```

This reduces gas costs by ~90% compared to individual anchors.

## Security Considerations

⚠️ **Important**: 
- Never commit `.env` files containing private keys
- Use a dedicated wallet with minimal funds for anchoring
- Consider using AWS KMS or similar for key management in production
- The zero-address destination (`0x00...0`) is standard for data anchoring

## Use Cases

- **ML Model Auditing**: Prove model predictions were made before an event occurred
- **Regulatory Compliance**: Immutable records for financial services
- **Prediction Markets**: Verifiable outcome resolution
- **Supply Chain**: Tamper-proof tracking of goods and predictions

## Dependencies

- `web3.py` - Ethereum/Polygon blockchain interaction
- `eth-account` - Transaction signing
- `python-dotenv` - Environment configuration
- `hexbytes` - Hex string handling

## License

MIT License - See LICENSE file for details

## Contact

For questions or contributions, please open an issue on GitHub.
