from pydantic import BaseModel
from typing import Optional


class CascadeSettings(BaseModel):
    ajax_scroll_auto: Optional[bool] = None

    class Config:
        orm_mode = True
