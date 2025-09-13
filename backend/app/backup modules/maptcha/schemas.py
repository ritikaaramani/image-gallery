from pydantic import BaseModel

class MaptchaCheckRequest(BaseModel):
    maptcha_response: int
    maptcha_requested: int
    maptcha_challenge: str
