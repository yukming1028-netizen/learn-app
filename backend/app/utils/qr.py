"""QR token generation and verification."""
import base64
import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.config import settings


def generate_qr_token(parent_id: int) -> tuple[str, datetime]:
    """Generate an encrypted QR binding token for a parent.
    Returns (token_string, expires_at).
    """
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.QR_TOKEN_EXPIRE_MINUTES)
    payload = {
        "parent_id": parent_id,
        "nonce": str(uuid.uuid4()),
        "exp": expires_at.isoformat(),
    }
    payload_json = json.dumps(payload, separators=(",", ":"))
    # Sign with HMAC-SHA256
    sig = hmac.new(
        settings.SECRET_KEY.encode(),
        payload_json.encode(),
        hashlib.sha256,
    ).hexdigest()
    # Combine payload + signature, base64 encode
    combined = json.dumps({"p": payload_json, "s": sig})
    token = base64.urlsafe_b64encode(combined.encode()).decode()
    return token, expires_at


def verify_qr_token(token: str) -> Optional[dict]:
    """Verify a QR token. Returns payload dict or None if invalid/expired."""
    try:
        combined = base64.urlsafe_b64decode(token.encode()).decode()
        data = json.loads(combined)
        payload_json = data["p"]
        sig = data["s"]

        # Verify signature
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            payload_json.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(sig, expected_sig):
            return None

        payload = json.loads(payload_json)
        # Check expiry
        expires_at = datetime.fromisoformat(payload["exp"])
        if datetime.now(timezone.utc) > expires_at:
            return None

        return payload
    except (KeyError, ValueError, json.JSONDecodeError):
        return None
