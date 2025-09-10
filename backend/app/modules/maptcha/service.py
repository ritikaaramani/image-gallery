import time
import hashlib
import random
from sqlalchemy.orm import Session
from app.modules.users import schemas
from app.modules.users.models import User as UserModel
import bcrypt


MAPTCHA_STORE = {}

def generate_challenge():
    """Generate a simple math captcha."""
    a, b = random.randint(1, 9), random.randint(1, 9)
    answer = a + b
    requested = int(time.time())
    challenge = hashlib.sha256(f"{a}{b}{requested}".encode()).hexdigest()

    MAPTCHA_STORE[challenge] = {"answer": answer, "requested": requested}

    return {
        "label": f"How much is {a} + {b}?",
        "requested": requested,
        "challenge": challenge,
    }

def verify_maptcha(maptcha_response: int, maptcha_requested: int, maptcha_challenge: str) -> bool:
    """Verify captcha input."""
    data = MAPTCHA_STORE.get(maptcha_challenge)
    if not data:
        return False
    if data["requested"] != maptcha_requested:
        return False
    return int(maptcha_response) == int(data["answer"])



