"""Short bind code generation and lookup (in-memory, TTL 5 min)."""
import random
import string
import time
from threading import Lock

# code -> {qr_token, parent_id, expires_at}
_BIND_CODES: dict[str, dict] = {}
_LOCK = Lock()

# Cleanup threshold
_MAX_CODES = 1000


def _gen_code() -> str:
    """Generate a 6-char alphanumeric code (no ambiguous chars)."""
    chars = string.ascii_uppercase + string.digits
    # Remove ambiguous: O, 0, I, 1, L
    chars = chars.replace("O", "").replace("0", "").replace("I", "").replace("1", "").replace("L", "")
    return "".join(random.choices(chars, k=6))


def store_bind_code(qr_token: str, parent_id: int, expires_at_ts: float) -> str:
    """Store a short code mapping to the QR token. Returns the code."""
    with _LOCK:
        # Cleanup expired
        now = time.time()
        expired = [k for k, v in _BIND_CODES.items() if v["expires_at_ts"] < now]
        for k in expired:
            del _BIND_CODES[k]

        # Generate unique code
        for _ in range(10):
            code = _gen_code()
            if code not in _BIND_CODES:
                break

        _BIND_CODES[code] = {
            "qr_token": qr_token,
            "parent_id": parent_id,
            "expires_at_ts": expires_at_ts,
        }
        return code


def lookup_bind_code(code: str) -> str | None:
    """Look up a bind code, return the qr_token if valid, else None."""
    with _LOCK:
        entry = _BIND_CODES.get(code.upper().strip())
        if not entry:
            return None
        if time.time() > entry["expires_at_ts"]:
            del _BIND_CODES[code.upper().strip()]
            return None
        return entry["qr_token"]
