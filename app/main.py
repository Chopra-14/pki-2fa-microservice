from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

from app.crypto_utils import load_private_key, decrypt_seed
from app.totp_utils import generate_totp_with_validity, verify_totp_code

app = FastAPI()

DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"

class EncryptedSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: Optional[str] = None

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(payload: EncryptedSeedRequest):
    encrypted_seed_b64 = payload.encrypted_seed.strip()

    try:
        private_key = load_private_key()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load private key")
    try:
        hex_seed = decrypt_seed(encrypted_seed_b64, private_key)
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        SEED_FILE.write_text(hex_seed, encoding="utf-8")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save seed")

    return {"status": "ok"}


@app.get("/generate-2fa")
def generate_2fa():
   
    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

 
    try:
        hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read seed")

    try:
        code, valid_for = generate_totp_with_validity(hex_seed)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate TOTP")

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
def verify_2fa(payload: VerifyRequest):

    if payload.code is None or payload.code.strip() == "":
        raise HTTPException(status_code=400, detail="Missing code")

    code = payload.code.strip()

    
    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    
    try:
        hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read seed")

    try:
        is_valid = verify_totp_code(hex_seed, code, valid_window=1)
    except Exception:
        raise HTTPException(status_code=500, detail="Verification failed")

    return {"valid": is_valid}


@app.get("/health")
def health():
    return {"status": "ok"}