from fastapi import Request, Response
import time
from app.modules.cacher.service import CacherService

service = CacherService()

async def cacher_middleware(request: Request, call_next):
    if not service.is_eligible(request):
        return await call_next(request)
    
    ims = request.headers.get("if-modified-since")
    lastmod = service.get_lastmod()
    if ims:
        try:
            ims_time = int(time.mktime(time.strptime(ims, "%a, %d %b %Y %H:%M:%S %Z")))
            if ims_time >= lastmod:
                return Response(status_code=304)
        except:
            pass

    if service.validate_etag(request):
        return Response(status_code=304)

    response = await call_next(request)

    response.headers["Last-Modified"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(lastmod))
    response.headers["Cache-Control"] = "no-cache, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(lastmod + 30*24*60*60))
    response.headers["ETag"] = service.generate_etag(request)
    response.headers["Vary"] = "Accept-Encoding, Cookie, Save-Data, ETag"

    return response
