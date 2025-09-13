# app/modules/sitemap/sitemap.py
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from datetime import datetime, timezone
import importlib
from typing import List, Any, Optional
import logging
import os

router = APIRouter(prefix="/sitemap", tags=["Sitemap"])
log = logging.getLogger("sitemap")

# Config (override with env vars or app config in production)
BASE_URL = os.getenv("SITEMAP_BASE_URL", "http://localhost:8000").rstrip("/")
SITEMAP_SETTINGS = {
    "root_changefreq": os.getenv("SITEMAP_ROOT_CHANGEFREQ", "daily"),
    "images_changefreq": os.getenv("SITEMAP_IMAGES_CHANGEFREQ", "weekly"),
    "albums_changefreq": os.getenv("SITEMAP_ALBUMS_CHANGEFREQ", "monthly"),
    "pages_changefreq": os.getenv("SITEMAP_PAGES_CHANGEFREQ", "yearly"),
    "max_items": int(os.getenv("SITEMAP_MAX_ITEMS", "2000")),
}


def _safe_iso(dt: Optional[datetime]) -> str:
    if not dt:
        return datetime.now(timezone.utc).isoformat()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _model_url(obj: Any, base: str, prefix: str, id_attr: str = "id") -> Optional[str]:
    """
    Try to obtain the public URL for an object in several ways:
      - If obj has `url` attribute, return it (assumed absolute or relative)
      - If obj has a `url(base_url)` or `url()` method, call it
      - Otherwise construct as f"{base}/{prefix}/{id}"
    Returns None if required id is missing.
    """
    # Prefer explicit url field
    if getattr(obj, "url", None):
        return str(obj.url)

    # If model has a url() method that accepts a base string -> call it
    url_method = getattr(obj, "url", None)
    if callable(url_method):
        try:
            # some models expect base_url param, some don't
            try:
                return url_method(base)
            except TypeError:
                return url_method()
        except Exception:
            pass

    # fallback to id attribute
    obj_id = getattr(obj, id_attr, None)
    if not obj_id:
        return None
    return f"{base}/{prefix}/{obj_id}"


def _safe_list_query(db: Session, model, filter_expr=None, limit: int = 1000, order_by=None) -> List[Any]:
    q = db.query(model)
    if filter_expr is not None:
        q = q.filter(filter_expr)
    if order_by is not None:
        q = q.order_by(order_by)
    return q.limit(limit).all()


@router.get("/sitemap.xml", response_class=Response)
def generate_sitemap(db: Session = Depends(get_db)):
    """
    Sitemap generator that includes:
      - root "/"
      - images (from uploads or images module)
      - albums (from gallery/albums module)
      - pages / posts (if present, for backward compatibility)
    """
    try:
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        # -- root
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{BASE_URL}/</loc>")
        xml_lines.append(f"    <lastmod>{datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()}</lastmod>")
        xml_lines.append(f"    <changefreq>{SITEMAP_SETTINGS['root_changefreq']}</changefreq>")
        xml_lines.append("    <priority>1.0</priority>")
        xml_lines.append("  </url>")

        items_added = 1

        # --- Helper to attempt import of model from multiple candidate modules/names
        def try_import_model(candidates: List[str]):
            for path in candidates:
                try:
                    module_name, class_name = path.rsplit(".", 1)
                    mod = importlib.import_module(module_name)
                    cls = getattr(mod, class_name)
                    return cls
                except Exception:
                    continue
            return None

        '''# --- Images: look in uploads.Upload, images.Image, uploads.models.Upload
        ImageModel = try_import_model([
            "app.modules.uploads.models.Upload",
            "app.modules.images.models.Image",
            "app.modules.media.models.Image",
        ])

        if ImageModel:
            try:
                images = db.query(ImageModel).limit(SITEMAP_SETTINGS["max_items"]).all()
            except Exception as e:
                log.exception("Failed to query images for sitemap: %s", e)
                images = []
            for img in images:
                loc = _model_url(img, BASE_URL, "images", id_attr="id")
                if not loc:
                    continue
                lastmod = getattr(img, "uploaded_at", None) or getattr(img, "updated_at", None) or getattr(img, "created_at", None)
                xml_lines.append("  <url>")
                xml_lines.append(f"    <loc>{loc}</loc>")
                xml_lines.append(f"    <lastmod>{_safe_iso(lastmod)}</lastmod>")
                xml_lines.append(f"    <changefreq>{SITEMAP_SETTINGS['images_changefreq']}</changefreq>")
                xml_lines.append("    <priority>0.7</priority>")
                xml_lines.append("  </url>")
                items_added += 1
        else:
            log.debug("No Image model found for sitemap (checked uploads.models.Upload and images.models.Image)")'''

        # --- Albums: check common locations
        AlbumModel = try_import_model([
            "app.modules.gallery.models.Album",
            "app.modules.albums.models.Album",
            "app.modules.gallery.models.Collection",
        ])

        if AlbumModel:
            try:
                albums = db.query(AlbumModel).limit(SITEMAP_SETTINGS["max_items"]).all()
            except Exception as e:
                log.exception("Failed to query albums for sitemap: %s", e)
                albums = []
            for alb in albums:
                loc = _model_url(alb, BASE_URL, "albums", id_attr="id")
                if not loc:
                    continue
                lastmod = getattr(alb, "updated_at", None) or getattr(alb, "created_at", None)
                xml_lines.append("  <url>")
                xml_lines.append(f"    <loc>{loc}</loc>")
                xml_lines.append(f"    <lastmod>{_safe_iso(lastmod)}</lastmod>")
                xml_lines.append(f"    <changefreq>{SITEMAP_SETTINGS['albums_changefreq']}</changefreq>")
                xml_lines.append("    <priority>0.6</priority>")
                xml_lines.append("  </url>")
                items_added += 1
        else:
            log.debug("No Album model found for sitemap (checked gallery.models.Album and albums.models.Album)")

        # --- Backwards compatibility: include posts/pages if present
        PostModel = try_import_model([
            "app.modules.posts.models.Post",
        ])
        PageModel = try_import_model([
            "app.modules.pages.models.Page",
        ])

        if PostModel:
            try:
                posts = db.query(PostModel).filter(getattr(PostModel, "status", None) == "public").limit(SITEMAP_SETTINGS["max_items"]).all()
            except Exception:
                posts = db.query(PostModel).limit(SITEMAP_SETTINGS["max_items"]).all()
            for p in posts:
                loc = _model_url(p, BASE_URL, "posts", id_attr="id")
                if not loc:
                    continue
                lastmod = getattr(p, "updated_at", None) or getattr(p, "created_at", None)
                xml_lines.append("  <url>")
                xml_lines.append(f"    <loc>{loc}</loc>")
                xml_lines.append(f"    <lastmod>{_safe_iso(lastmod)}</lastmod>")
                xml_lines.append(f"    <changefreq>{SITEMAP_SETTINGS['pages_changefreq']}</changefreq>")
                xml_lines.append("    <priority>0.5</priority>")
                xml_lines.append("  </url>")
                items_added += 1

        if PageModel:
            try:
                pages = db.query(PageModel).filter(getattr(PageModel, "public", None) == True).limit(SITEMAP_SETTINGS["max_items"]).all()
            except Exception:
                pages = db.query(PageModel).limit(SITEMAP_SETTINGS["max_items"]).all()
            for page in pages:
                loc = _model_url(page, BASE_URL, "pages", id_attr="id")
                if not loc:
                    continue
                lastmod = getattr(page, "updated_at", None) or getattr(page, "created_at", None)
                priority = "1.0" if getattr(page, "show_in_list", False) else "0.5"
                xml_lines.append("  <url>")
                xml_lines.append(f"    <loc>{loc}</loc>")
                xml_lines.append(f"    <lastmod>{_safe_iso(lastmod)}</lastmod>")
                xml_lines.append(f"    <changefreq>{SITEMAP_SETTINGS['pages_changefreq']}</changefreq>")
                xml_lines.append(f"    <priority>{priority}</priority>")
                xml_lines.append("  </url>")
                items_added += 1

        xml_lines.append("</urlset>")
        xml_content = "\n".join(xml_lines)
        return Response(content=xml_content, media_type="application/xml")
    
    finally:
        # Always close the database session
        db.close()
