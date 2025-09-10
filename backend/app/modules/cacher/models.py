from pydantic import BaseModel

class CacherSettings(BaseModel):
    cache_lastmod: int
