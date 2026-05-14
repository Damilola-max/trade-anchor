import os, requests
from dotenv import load_dotenv
load_dotenv()

PINATA_JWT = os.getenv("PINATA_JWT")

def ipfs_add_bytes(name: str, data: bytes) -> dict:
    """Upload file or JSON to IPFS using Pinata."""
    if not PINATA_JWT:
        raise RuntimeError("Missing PINATA_JWT in .env")
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {"Authorization": f"Bearer {PINATA_JWT}"}
    files = {'file': (name, data)}
    r = requests.post(url, headers=headers, files=files, timeout=60)
    r.raise_for_status()
    j = r.json()
    return {"Name": name, "Hash": j["IpfsHash"], "Size": str(len(data))}
