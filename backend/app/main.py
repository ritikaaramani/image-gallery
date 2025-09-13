from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

from app.modules.maptcha.router import router as maptcha_router
from app.modules.users.router import router as users_router
from app.modules.sitemap.sitemap import router as sitemap_router
from app.modules.pages.router import router as pages_router
from app.modules.cacher.router import router as cacher_router
from app.modules.cascade.router import router as cascade_router
from app.middleware.cacher_middleware import cacher_middleware
from app.modules.read_more.router import router as read_more_router
from app.modules.feeds.router import router as feeds_router
from app.modules.search.router import router as search_router
from app.modules.uploads.router import router as uploads_router
from app.modules.images.router import router as images_router
from app.modules.albums.router import router as albums_router
from app.modules.image_views.router import router as image_views_router
from app.modules.image_likes.router import router as likes_router
from fastapi.middleware.cors import CORSMiddleware
from app.modules.comments.router import router as comments_router
from app.modules.gallery.router import router as gallery_router
from app.routes import ai


app = FastAPI(
    title="Image-gallery FastAPI Backend",
    description="Backend for Image gallery modules",
    version="1.0"
)
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")  # use cwd, not BASE_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


app.include_router(images_router, tags=["Images"])
app.include_router(albums_router, tags=["Albums"])
app.include_router(image_views_router, prefix="/image_views", tags=["Image Views"])
app.include_router(likes_router, prefix="/likes", tags=["Likes"])
app.include_router(users_router, tags=["Users"])
app.include_router(sitemap_router)
app.include_router(pages_router)
app.include_router(maptcha_router)
app.include_router(cacher_router, prefix="/cacher", tags=["Cacher"])
app.include_router(cascade_router, prefix="/cascade", tags=["Cascade"])
app.include_router(read_more_router)
app.include_router(feeds_router)
app.include_router(search_router)
app.include_router(uploads_router)
app.include_router(comments_router, prefix="/comments", tags=["Comments"])
app.include_router(ai.router)
app.include_router(gallery_router, prefix="", tags=["Gallery"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(cacher_middleware)

@app.get("/")
def read_root():
    return {"message": "Hello! FastAPI is running."}
