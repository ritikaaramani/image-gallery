# app/modules/search/service.py - Minimal working version
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text, func
from datetime import datetime, timezone
import importlib
from typing import List, Any, Optional
from . import schemas
import logging
import json

log = logging.getLogger("search")


def try_import_model(candidates):
    """Try to import a model given a list of fully-qualified strings "module.Class"."""
    for path in candidates:
        try:
            module_name, class_name = path.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
            return cls
        except (ImportError, AttributeError, ValueError) as e:
            log.debug(f"Failed to import {path}: {e}")
            continue
    return None


def _safe_created_at(obj: Any) -> datetime:
    """Return a datetime for sorting (prefer common fields)."""
    for attr in ("created_at", "uploaded_at", "updated_at"):
        val = getattr(obj, attr, None)
        if val is not None and isinstance(val, datetime):
            return val
    return datetime.now(timezone.utc)


def _safe_excerpt(text: Any, max_len: int = 200) -> str:
    """Create a safe excerpt from text."""
    if not text:
        return ""
    s = str(text).strip()
    if len(s) <= max_len:
        return s
    # Find last space within limit to avoid cutting words
    truncated = s[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len * 0.8:  # Only use space if it's not too far back
        return truncated[:last_space] + "..."
    return truncated + "..."


def _parse_tags_field(tags_field) -> List[str]:
    """Normalize tags field (JSON, list, or CSV string) into a list of strings."""
    if tags_field is None:
        return []
    
    try:
        # Handle list input
        if isinstance(tags_field, list):
            return [str(t).strip() for t in tags_field if str(t).strip()]

        # Handle string input
        if isinstance(tags_field, str):
            tags_field = tags_field.strip()
            if not tags_field:
                return []
                
            # Try JSON parsing first
            if tags_field.startswith("[") and tags_field.endswith("]"):
                try:
                    parsed = json.loads(tags_field)
                    if isinstance(parsed, list):
                        return [str(t).strip() for t in parsed if str(t).strip()]
                except (json.JSONDecodeError, ValueError):
                    pass
            
            # Fall back to CSV parsing
            return [t.strip() for t in tags_field.split(",") if t.strip()]
            
    except Exception as e:
        log.debug(f"Failed to parse tags field {tags_field}: {e}")
    
    return []


def _has_column(model, column_name: str) -> bool:
    """Check if a model has a specific column."""
    try:
        if not hasattr(model, '__table__'):
            return False
        return column_name in model.__table__.columns
    except Exception:
        return False


def _build_search_filters(model, query: str, search_fields: List[str]):
    """Build search filters for a model, only using existing columns."""
    filters = []
    query_pattern = f"%{query}%"
    
    for field_name in search_fields:
        if _has_column(model, field_name):
            try:
                field = getattr(model, field_name)
                filters.append(field.ilike(query_pattern))
            except Exception as e:
                log.debug(f"Failed to create filter for {field_name}: {e}")
                continue
    
    return filters


def search_content(db: Session, query: str, limit: int = 20) -> List[schemas.SearchResult]:
    """Search across different content types - only the ones that actually work."""
    if not query or not query.strip():
        return []
    
    query = query.strip()
    results: List[schemas.SearchResult] = []

    # --- Search in Album model ---
    AlbumModel = try_import_model([
        "app.modules.albums.models.Album",
        "app.modules.albums.models.PhotoAlbum"
    ])
    if AlbumModel:
        try:
            # Correct search fields for the Album model
            search_fields = ["title", "description"]
            filters = _build_search_filters(AlbumModel, query, search_fields)
            
            if filters:
                albums = (
                    db.query(AlbumModel)
                    .filter(or_(*filters))
                    .limit(limit)
                    .all()
                )
                
                for album in albums:
                    title = (
                        getattr(album, "title", None) or 
                        f"Album {getattr(album, 'id', 'Unknown')}"
                    )
                    
                    results.append(
                        schemas.SearchResult(
                            id=str(getattr(album, "id", "")),
                            type=schemas.ContentType.ALBUM,
                            title=title,
                            excerpt=_safe_excerpt(getattr(album, "description", "")),
                            created_at=_safe_created_at(album),
                            url=f"/albums/{getattr(album, 'id', '')}",
                            thumbnail_url=getattr(album, "cover_image_url", None),
                            tags=_parse_tags_field(getattr(album, "tags", None)),
                        )
                    )
        except Exception as e:
            db.rollback()
            log.exception("Album search failed for query '%s': %s", query, e)

    # --- Search in Image model (WORKING) ---
    ImageModel = try_import_model(["app.modules.images.models.Image"])
    if ImageModel:
        try:
            search_fields = ["title", "description", "caption", "filename"]
            filters = _build_search_filters(ImageModel, query, search_fields)
            
            if filters:
                images = (
                    db.query(ImageModel)
                    .filter(or_(*filters))
                    .limit(limit)
                    .all()
                )
                
                for img in images:
                    title = getattr(img, "title", None) or getattr(img, "filename", None) or f"Image {getattr(img, 'id', 'Unknown')}"
                    
                    results.append(
                        schemas.SearchResult(
                            id=str(getattr(img, "id", "")),
                            type=schemas.ContentType.IMAGE,
                            title=title,
                            excerpt=_safe_excerpt(getattr(img, "description", "") or getattr(img, "caption", "")),
                            created_at=_safe_created_at(img),
                            url=f"/images/{getattr(img, 'id', '')}",
                            thumbnail_url=None,
                            tags=[],
                        )
                    )
        except Exception as e:
            db.rollback()
            log.exception("Image search failed for query '%s': %s", query, e)
    
    # --- Search in Upload model (WORKING) ---
    UploadModel = try_import_model(["app.modules.uploads.models.Upload"])
    if UploadModel:
        try:
            search_fields = ["filename", "description"]
            filters = _build_search_filters(UploadModel, query, search_fields)
            
            if filters:
                uploads = (
                    db.query(UploadModel)
                    .filter(or_(*filters))
                    .limit(limit)
                    .all()
                )
                
                for upload in uploads:
                    title = getattr(upload, "filename", None) or f"Upload {getattr(upload, 'id', 'Unknown')}"
                    
                    results.append(
                        schemas.SearchResult(
                            id=str(getattr(upload, "id", "")),
                            type=schemas.ContentType.UPLOAD,
                            title=title,
                            excerpt=_safe_excerpt(getattr(upload, "description", "")),
                            created_at=_safe_created_at(upload),
                            url=getattr(upload, "url", None),
                            thumbnail_url=getattr(upload, "thumbnail_url", None),
                            tags=_parse_tags_field(getattr(upload, "tags", None)),
                        )
                    )
        except Exception as e:
            db.rollback()
            log.exception("Upload search failed for query '%s': %s", query, e)

    # --- Search in Comment model ---
    CommentModel = try_import_model(["app.modules.comments.models.Comment"])
    if CommentModel:
        try:
            # Correct search fields for the Comment model
            search_fields = ["content"]
            filters = _build_search_filters(CommentModel, query, search_fields)
            
            if filters:
                comments = (
                    db.query(CommentModel)
                    .filter(or_(*filters))
                    .limit(limit)
                    .all()
                )
                
                for comment in comments:
                    content = getattr(comment, "content", None) or getattr(comment, "text", None) or getattr(comment, "body", None)
                    title = f"Comment by {getattr(comment, 'author_name', 'User')}" if hasattr(comment, 'author_name') else "Comment"
                    
                    results.append(
                        schemas.SearchResult(
                            id=str(getattr(comment, "id", "")),
                            type=schemas.ContentType.COMMENT,
                            title=title,
                            excerpt=_safe_excerpt(content),
                            created_at=_safe_created_at(comment),
                            url=f"/comments/{getattr(comment, 'id', '')}",
                            thumbnail_url=None,
                            tags=[],
                        )
                    )
        except Exception as e:
            db.rollback()
            log.exception("Comment search failed for query '%s': %s", query, e)

    # --- Search in User model ---
    UserModel = try_import_model(["app.modules.users.models.User"])
    if UserModel:
        try:
            # Correct search fields for the User model
            search_fields = ["username", "email"]
            filters = _build_search_filters(UserModel, query, search_fields)
            
            if filters:
                users = (
                    db.query(UserModel)
                    .filter(or_(*filters))
                    .limit(limit)
                    .all()
                )
                
                for user in users:
                    title = (
                        getattr(user, "username", None) or 
                        f"User {getattr(user, 'id', 'Unknown')}"
                    )
                    
                    results.append(
                        schemas.SearchResult(
                            id=str(getattr(user, "id", "")),
                            type=schemas.ContentType.USER,
                            title=title,
                            excerpt=_safe_excerpt(getattr(user, "bio", "")),
                            created_at=_safe_created_at(user),
                            url=f"/users/{getattr(user, 'id', '')}",
                            thumbnail_url=getattr(user, "avatar_url", None),
                            tags=[],
                        )
                    )
        except Exception as e:
            db.rollback()
            log.exception("User search failed for query '%s': %s", query, e)

    # --- Search in Pages (WORKING) ---
    PageModel = try_import_model(["app.modules.pages.models.Page"])
    if PageModel:
        try:
            search_fields = ["title", "content"]
            filters = _build_search_filters(PageModel, query, search_fields)
            
            if filters:
                pages = (
                    db.query(PageModel)
                    .filter(or_(*filters))
                    .limit(limit)
                    .all()
                )
                
                for page in pages:
                    title = getattr(page, "title", None) or f"Page {getattr(page, 'id', 'Unknown')}"
                    
                    results.append(
                        schemas.SearchResult(
                            id=str(getattr(page, "id", "")),
                            type=schemas.ContentType.PAGE,
                            title=title,
                            excerpt=_safe_excerpt(getattr(page, "content", "")),
                            created_at=_safe_created_at(page),
                            url=getattr(page, "url", None) or f"/pages/{getattr(page, 'id', '')}",
                            tags=[],
                        )
                    )
        except Exception as e:
            db.rollback()
            log.exception("Page search failed for query '%s': %s", query, e)

    # --- Sort all results by date, newest first ---
    try:
        results.sort(key=lambda r: r.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    except Exception as e:
        log.warning("Failed to sort search results: %s", e)
    
    return results[:limit]


def search_by_type(db: Session, query: str, content_type: str, limit: int = 20) -> List[schemas.SearchResult]:
    """Search within a specific content type."""
    # Simple approach - get all results and filter
    all_results = search_content(db, query, limit * 3)
    
    # Filter by type - handle both string and enum types
    filtered_results = []
    for r in all_results:
        result_type = r.type.value if hasattr(r.type, 'value') else str(r.type)
        if result_type == content_type:
            filtered_results.append(r)
    
    return filtered_results[:limit]

# New function: get_search_suggestions
def get_search_suggestions(db: Session, query: str, limit: int = 5) -> List[schemas.SearchSuggestion]:
    """Generate search suggestions based on partial query matches."""
    suggestions = []
    
    # Use a set to store unique suggestions
    unique_suggestions = set()
    query_ilike = f"{query.lower()}%"
    
    # --- Images (search on title and tags) ---
    ImageModel = try_import_model(["app.modules.images.models.Image"])
    if ImageModel:
        try:
            # Query for titles that start with the query string
            titles = db.query(ImageModel.title).filter(func.lower(ImageModel.title).like(query_ilike)).limit(limit).all()
            for t in titles:
                if t.title not in unique_suggestions:
                    suggestions.append(schemas.SearchSuggestion(text=t.title, type=schemas.ContentType.IMAGE))
                    unique_suggestions.add(t.title)
        except Exception as e:
            log.debug(f"Suggestions query for images failed: {e}")
            
    # --- Albums (search on title) ---
    AlbumModel = try_import_model(["app.modules.albums.models.Album"])
    if AlbumModel:
        try:
            titles = db.query(AlbumModel.title).filter(func.lower(AlbumModel.title).like(query_ilike)).limit(limit).all()
            for t in titles:
                if t.title not in unique_suggestions:
                    suggestions.append(schemas.SearchSuggestion(text=t.title, type=schemas.ContentType.ALBUM))
                    unique_suggestions.add(t.title)
        except Exception as e:
            log.debug(f"Suggestions query for albums failed: {e}")

    # --- Users (search on username) ---
    UserModel = try_import_model(["app.modules.users.models.User"])
    if UserModel:
        try:
            usernames = db.query(UserModel.username).filter(func.lower(UserModel.username).like(query_ilike)).limit(limit).all()
            for u in usernames:
                if u.username not in unique_suggestions:
                    suggestions.append(schemas.SearchSuggestion(text=u.username, type=schemas.ContentType.USER))
                    unique_suggestions.add(u.username)
        except Exception as e:
            log.debug(f"Suggestions query for users failed: {e}")
    
    return suggestions[:limit]

# New function: get_popular_searches
def get_popular_searches(db: Session, limit: int = 10) -> List[str]:
    """
    Get popular search terms based on most common titles/tags.
    This is a placeholder as a dedicated analytics table doesn't exist.
    """
    popular_terms = []
    unique_terms = set()
    
    # --- Popular titles from Images ---
    ImageModel = try_import_model(["app.modules.images.models.Image"])
    if ImageModel:
        try:
            titles = (
                db.query(ImageModel.title, func.count(ImageModel.title))
                .filter(ImageModel.title != None)
                .group_by(ImageModel.title)
                .order_by(func.count(ImageModel.title).desc())
                .limit(limit)
                .all()
            )
            for title, count in titles:
                if title not in unique_terms:
                    popular_terms.append(title)
                    unique_terms.add(title)
        except Exception as e:
            log.debug(f"Popular search query for images failed: {e}")

    # --- Popular titles from Albums ---
    AlbumModel = try_import_model(["app.modules.albums.models.Album"])
    if AlbumModel:
        try:
            titles = (
                db.query(AlbumModel.title, func.count(AlbumModel.title))
                .filter(AlbumModel.title != None)
                .group_by(AlbumModel.title)
                .order_by(func.count(AlbumModel.title).desc())
                .limit(limit)
                .all()
            )
            for title, count in titles:
                if title not in unique_terms:
                    popular_terms.append(title)
                    unique_terms.add(title)
        except Exception as e:
            log.debug(f"Popular search query for albums failed: {e}")
    
    return popular_terms[:limit]


def get_search_stats(db: Session) -> dict:
    """Get search statistics for available content."""
    stats = {
        "total_searchable_content": 0,
        "content_types": {},
        "search_enabled": True
    }
    
    try:
        # Count images (we know this works)
        ImageModel = try_import_model(["app.modules.images.models.Image"])
        if ImageModel:
            image_count = db.query(ImageModel).count()
            stats["content_types"]["images"] = image_count
            stats["total_searchable_content"] += image_count
        
        # Count uploads (we know this works)
        UploadModel = try_import_model(["app.modules.uploads.models.Upload"])
        if UploadModel:
            try:
                upload_count = db.query(UploadModel).count()
                stats["content_types"]["uploads"] = upload_count
                stats["total_searchable_content"] += upload_count
            except Exception:
                pass
        
        # Count albums (if exists)
        AlbumModel = try_import_model([
            "app.modules.albums.models.Album",
            "app.modules.albums.models.PhotoAlbum"
        ])
        if AlbumModel:
            try:
                album_count = db.query(AlbumModel).count()
                stats["content_types"]["albums"] = album_count
                stats["total_searchable_content"] += album_count
            except Exception:
                pass
        
        # Count comments (if exists)
        CommentModel = try_import_model(["app.modules.comments.models.Comment"])
        if CommentModel:
            try:
                comment_count = db.query(CommentModel).count()
                stats["content_types"]["comments"] = comment_count
                stats["total_searchable_content"] += comment_count
            except Exception:
                pass
        
        # Count users (if exists)
        UserModel = try_import_model(["app.modules.users.models.User"])
        if UserModel:
            try:
                user_count = db.query(UserModel).count()
                stats["content_types"]["users"] = user_count
                stats["total_searchable_content"] += user_count
            except Exception:
                pass
        
        # Count pages (if exists)
        PageModel = try_import_model(["app.modules.pages.models.Page"])
        if PageModel:
            try:
                page_count = db.query(PageModel).count()
                stats["content_types"]["pages"] = page_count
                stats["total_searchable_content"] += page_count
            except Exception:
                pass
            
    except Exception as e:
        log.exception("Failed to get search stats: %s", e)
        stats["search_enabled"] = False
    
    return stats
