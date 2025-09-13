# app/modules/search/router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from . import service, schemas
from typing import List, Optional
import logging
import traceback

log = logging.getLogger("search")

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_model=List[schemas.SearchResult])
def search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    content_type: Optional[str] = Query(None, regex="^(album|image|upload|comment|user|page)$", description="Filter by content type"),
    db: Session = Depends(get_db),
):
    """
    Search across all content types or filter by specific type.
    
    **Available content types:**
    - **album**: Photo albums and collections
    - **image**: Individual images and photos
    - **upload**: File uploads
    - **comment**: User comments
    - **user**: User profiles (public info only)
    - **page**: Static pages and content
    
    **Parameters:**
    - **q**: Search query (1-500 characters)
    - **limit**: Maximum number of results (1-100, default: 20)
    - **content_type**: Optional filter by content type
    
    **Returns:** List of search results with metadata
    """
    try:
        # Validate and clean query
        query = q.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        # Log search for analytics (optional)
        log.info(f"Search query: '{query}', type: {content_type}, limit: {limit}")
        
        # Search with or without type filter
        if content_type:
            results = service.search_by_type(db, query, content_type, limit)
        else:
            results = service.search_content(db, query, limit)
        
        log.info(f"Search successful: returned {len(results)} results")
        return results
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        log.exception(f"Search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search service temporarily unavailable"
        )

@router.get("/debug")
def debug_search(
    q: str = Query("test", description="Debug search query"),
    db: Session = Depends(get_db),
):
    """
    Debug endpoint to test search functionality step by step.
    Remove this endpoint in production.
    """
    debug_info = {
        "query": q,
        "models_tested": {},
        "search_results": [],
        "errors": []
    }
    
    # Test model imports
    models_to_test = [
        ("Album", ["app.modules.albums.models.Album", "app.modules.albums.models.PhotoAlbum"]),
        ("Image", ["app.modules.images.models.Image"]),
        ("Upload", ["app.modules.uploads.models.Upload"]),
        ("Comment", ["app.modules.comments.models.Comment"]),
        ("User", ["app.modules.users.models.User"]),
        ("Page", ["app.modules.pages.models.Page"]),
    ]
    
    for model_name, candidates in models_to_test:
        try:
            model = service.try_import_model(candidates)
            if model:
                debug_info["models_tested"][model_name] = {
                    "imported": True,
                    "model_class": str(model),
                    "table_name": getattr(model.__table__, 'name', 'Unknown') if hasattr(model, '__table__') else 'No table',
                    "columns": list(model.__table__.columns.keys()) if hasattr(model, '__table__') else []
                }
                
                # Test database query
                try:
                    count = db.query(model).count()
                    debug_info["models_tested"][model_name]["record_count"] = count
                    
                    if count > 0:
                        sample = db.query(model).first()
                        debug_info["models_tested"][model_name]["sample_id"] = getattr(sample, 'id', 'No ID')
                        
                except Exception as db_error:
                    debug_info["models_tested"][model_name]["database_error"] = str(db_error)
                    debug_info["errors"].append(f"{model_name} database error: {db_error}")
                    
            else:
                debug_info["models_tested"][model_name] = {
                    "imported": False,
                    "error": "Could not import any candidate paths"
                }
                debug_info["errors"].append(f"Could not import {model_name}")
                
        except Exception as e:
            debug_info["models_tested"][model_name] = {
                "imported": False,
                "error": str(e)
            }
            debug_info["errors"].append(f"{model_name} import error: {e}")
    
    # Test actual search
    try:
        results = service.search_content(db, q, limit=5)
        debug_info["search_results"] = [
            {
                "id": r.id,
                "type": r.type.value,
                "title": r.title,
                "excerpt": r.excerpt[:100] + "..." if r.excerpt and len(r.excerpt) > 100 else r.excerpt
            }
            for r in results
        ]
        debug_info["search_success"] = True
        debug_info["total_results"] = len(results)
        
    except Exception as search_error:
        debug_info["search_success"] = False
        debug_info["search_error"] = str(search_error)
        debug_info["search_traceback"] = traceback.format_exc()
        debug_info["errors"].append(f"Search error: {search_error}")
    
    return debug_info

@router.get("/suggestions")
def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial search query"),
    limit: int = Query(5, ge=1, le=20, description="Max number of suggestions"),
    db: Session = Depends(get_db),
):
    """
    Get search suggestions based on partial query.
    
    **Parameters:**
    - **q**: Partial search query
    - **limit**: Maximum number of suggestions (1-20, default: 5)
    
    **Returns:** List of suggested search terms
    """
    try:
        query = q.strip()
        if not query:
            return {"suggestions": []}
        
        # This would need to be implemented in your service
        suggestions = service.get_search_suggestions(db, query, limit) if hasattr(service, 'get_search_suggestions') else []
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        log.exception(f"Search suggestions failed for query '{q}': {e}")
        return {"suggestions": []}  # Graceful fallback

@router.get("/popular")
def get_popular_searches(
    limit: int = Query(10, ge=1, le=50, description="Max number of popular searches"),
    content_type: Optional[str] = Query(None, regex="^(album|image|upload|comment|user|page)$", description="Filter by content type"),
):
    """
    Get popular search terms (if you track search analytics).
    
    **Parameters:**
    - **limit**: Maximum number of popular searches (1-50, default: 10)
    - **content_type**: Optional filter by content type
    
    **Returns:** List of popular search terms
    """
    try:
        # This would need analytics/tracking implementation
        # For now, return empty or mock data
        return {"popular_searches": []}
        
    except Exception as e:
        log.exception(f"Popular searches failed: {e}")
        return {"popular_searches": []}

@router.get("/stats")
def get_search_stats(db: Session = Depends(get_db)):
    """
    Get search statistics and available content counts.
    
    **Returns:** Search statistics and content type counts for your actual modules
    """
    try:
        stats = service.get_search_stats(db)
        return stats
        
    except Exception as e:
        log.exception(f"Search stats failed: {e}")
        return {
            "total_searchable_content": 0,
            "content_types": {},
            "search_enabled": False,
            "error": "Stats temporarily unavailable",
            "error_details": str(e)
        }

# Type-specific search endpoints (alternative to using query parameter)
@router.get("/albums", response_model=List[schemas.SearchResult])
def search_albums(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    db: Session = Depends(get_db),
):
    """Search only in albums."""
    try:
        query = q.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        log.info(f"Album-specific search: '{query}'")
        results = service.search_by_type(db, query, "album", limit)
        log.info(f"Album search successful: {len(results)} results")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Album search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Album search service temporarily unavailable"
        )

@router.get("/images", response_model=List[schemas.SearchResult])
def search_images(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    db: Session = Depends(get_db),
):
    """Search only in images."""
    try:
        query = q.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        log.info(f"Image-specific search: '{query}'")
        results = service.search_by_type(db, query, "image", limit)
        log.info(f"Image search successful: {len(results)} results")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Image search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image search service temporarily unavailable"
        )

@router.get("/uploads", response_model=List[schemas.SearchResult])
def search_uploads(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    db: Session = Depends(get_db),
):
    """Search only in uploads."""
    try:
        query = q.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        log.info(f"Upload-specific search: '{query}'")
        results = service.search_by_type(db, query, "upload", limit)
        log.info(f"Upload search successful: {len(results)} results")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Upload search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload search service temporarily unavailable"
        )

@router.get("/comments", response_model=List[schemas.SearchResult])
def search_comments(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    db: Session = Depends(get_db),
):
    """Search only in comments."""
    try:
        query = q.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        log.info(f"Comment-specific search: '{query}'")
        results = service.search_by_type(db, query, "comment", limit)
        log.info(f"Comment search successful: {len(results)} results")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Comment search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comment search service temporarily unavailable"
        )

@router.get("/users", response_model=List[schemas.SearchResult])
def search_users(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    db: Session = Depends(get_db),
):
    """Search only in users."""
    try:
        query = q.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        log.info(f"User-specific search: '{query}'")
        results = service.search_by_type(db, query, "user", limit)
        log.info(f"User search successful: {len(results)} results")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"User search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User search service temporarily unavailable"
        )

@router.get("/pages", response_model=List[schemas.SearchResult])
def search_pages(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max number of results"),
    db: Session = Depends(get_db),
):
    """Search only in pages."""
    try:
        query = q.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        log.info(f"Page-specific search: '{query}'")
        results = service.search_by_type(db, query, "page", limit)
        log.info(f"Page search successful: {len(results)} results")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Page search failed for query '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Page search service temporarily unavailable"
        )
