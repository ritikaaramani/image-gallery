# backend/app/utils.py
import os
from PIL import Image
from io import BytesIO

GENERATED_DIR = os.path.join(os.getcwd(), "generated")
THUMB_DIR = os.path.join(GENERATED_DIR, "thumbs")
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

def save_image_bytes(data: bytes, basename: str):
    path = os.path.join(GENERATED_DIR, basename)
    with open(path, "wb") as f:
        f.write(data)
    return path

def make_thumbnail(data: bytes, thumb_name: str, size=(320,320)):
    im = Image.open(BytesIO(data))
    im.thumbnail(size)
    path = os.path.join(THUMB_DIR, thumb_name)
    im.save(path, format="JPEG", quality=85)
    return path

def simple_safety_check(data: bytes) -> dict:
    """
    Placeholder safety check. Return dict {'nsfw': bool, 'score': float}
    Replace with nsfw_detector or HuggingFace SafetyChecker for production.
    """
    # naive placeholder: always safe
    return {"nsfw": False, "score": 0.0}
