from fastapi import FastAPI, Request
import uvicorn
from canonical_hash import normalize_trade, canonical_json, sha256_hex_of_canonical_obj

app = FastAPI()

@app.post("/normalize-trade")
async def normalize_trade_api(request: Request):
    raw = await request.json()
    canon = normalize_trade(raw)
    canon_str = canonical_json(canon)
    sha = sha256_hex_of_canonical_obj(canon)
    return {"canonical_json": canon_str, "sha256": sha}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
