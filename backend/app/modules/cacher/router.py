from fastapi import APIRouter
from .service import CacherService
from app.modules.cacher import service

router = APIRouter(prefix="/cache", tags=["Cacher"])
service_instance = CacherService()

@router.post("/regenerate")
def regenerate_cache():
    """
    Manual trigger for cache regeneration
    """
    service_instance.update_lastmod()
    return {"detail": "Cache regenerated"}

@router.post("/exclude")
def exclude_cache():
    """
    Mark current request as excluded from caching
    """
    service_instance.excluded = True
    return {"detail": "Cache excluded", "excluded": service_instance.excluded}
