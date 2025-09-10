# app/modules/pages/schemas.py
import uuid
from pydantic import BaseModel
from datetime import datetime

class PageBase(BaseModel):
    title: str
    slug: str
    content: str | None = None

class PageCreate(PageBase):
    pass

class Page(PageBase):
    id: uuid.UUID
    created_at: datetime
    # New fields to add
    public: bool
    show_in_list: bool

    model_config = {
        "from_attributes": True
    }
