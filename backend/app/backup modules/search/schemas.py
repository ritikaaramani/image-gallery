# app/modules/search/schemas.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal, Union
from enum import Enum

# Enum for content types to ensure consistency
class ContentType(str, Enum):
    ALBUM = "album"
    IMAGE = "image"
    UPLOAD = "upload"
    COMMENT = "comment" 
    USER = "user"
    PAGE = "page"

class SearchResult(BaseModel):
    id: str = Field(..., description="Unique identifier for the content")
    type: ContentType = Field(..., description="Type of content (image, album, page, etc.)")
    title: Optional[str] = Field(None, description="Title of the content")
    excerpt: Optional[str] = Field(None, max_length=500, description="Short excerpt or description")
    created_at: datetime = Field(..., description="When the content was created")
    updated_at: Optional[datetime] = Field(None, description="When the content was last updated")
    
    # URLs and links
    url: Optional[str] = Field(None, description="Direct URL to the content")
    thumbnail_url: Optional[str] = Field(None, description="URL to thumbnail image")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Content tags")
    author: Optional[str] = Field(None, description="Content author/creator")
    category: Optional[str] = Field(None, description="Content category")
    
    # Search-specific fields
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Search relevance score")
    matched_fields: Optional[List[str]] = Field(default_factory=list, description="Fields that matched the search")
    
    # Type-specific metadata (flexible JSON field)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Type-specific metadata")

    @validator('excerpt')
    def truncate_excerpt(cls, v):
        if v and len(v) > 500:
            return v[:497] + "..."
        return v

    @validator('tags')
    def ensure_tags_list(cls, v):
        if v is None:
            return []
        return [tag.strip() for tag in v if tag and tag.strip()]

    @validator('matched_fields')
    def ensure_matched_fields_list(cls, v):
        if v is None:
            return []
        return list(set(v))  # Remove duplicates

    class Config:
        orm_mode = True
        use_enum_values = True

# Specialized result types for different content
class AlbumSearchResult(SearchResult):
    type: Literal[ContentType.ALBUM] = ContentType.ALBUM
    cover_image_url: Optional[str] = Field(None, description="URL to album cover image")
    image_count: Optional[int] = Field(None, ge=0, description="Number of images in album")
    
class ImageSearchResult(SearchResult):
    type: Literal[ContentType.IMAGE] = ContentType.IMAGE
    width: Optional[int] = Field(None, ge=1, description="Image width in pixels")
    height: Optional[int] = Field(None, ge=1, description="Image height in pixels")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    format: Optional[str] = Field(None, description="Image format (jpg, png, etc.)")
    alt_text: Optional[str] = Field(None, description="Alt text for accessibility")

class UploadSearchResult(SearchResult):
    type: Literal[ContentType.UPLOAD] = ContentType.UPLOAD
    filename: Optional[str] = Field(None, description="Original filename")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type of the file")
    
class CommentSearchResult(SearchResult):
    type: Literal[ContentType.COMMENT] = ContentType.COMMENT
    author_name: Optional[str] = Field(None, description="Name of comment author")
    parent_id: Optional[str] = Field(None, description="ID of parent comment or content")
    
class UserSearchResult(SearchResult):
    type: Literal[ContentType.USER] = ContentType.USER
    username: Optional[str] = Field(None, description="Username")
    display_name: Optional[str] = Field(None, description="Display name")
    avatar_url: Optional[str] = Field(None, description="Profile avatar URL")
    
class PageSearchResult(SearchResult):
    type: Literal[ContentType.PAGE] = ContentType.PAGE
    slug: Optional[str] = Field(None, description="URL slug")
    parent_page: Optional[str] = Field(None, description="Parent page ID or title")
    menu_order: Optional[int] = Field(None, description="Order in navigation menu")

# Search request schemas
class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=500, description="Search query")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip (for pagination)")
    
    # Advanced search options
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    author: Optional[str] = Field(None, description="Filter by author")
    category: Optional[str] = Field(None, description="Filter by category")
    date_from: Optional[datetime] = Field(None, description="Filter content created after this date")
    date_to: Optional[datetime] = Field(None, description="Filter content created before this date")
    
    @validator('q')
    def clean_query(cls, v):
        return v.strip()
    
    @validator('tags')
    def clean_tags(cls, v):
        if not v:
            return None
        return [tag.strip().lower() for tag in v if tag and tag.strip()]

# Search response schemas
class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(description="Search results")
    total_count: int = Field(ge=0, description="Total number of matching results")
    page: int = Field(ge=1, description="Current page number")
    per_page: int = Field(ge=1, description="Results per page")
    has_more: bool = Field(description="Whether there are more results available")
    query: str = Field(description="Original search query")
    search_time: Optional[float] = Field(None, ge=0, description="Search execution time in seconds")
    
    # Facets for filtering
    facets: Optional[Dict[str, List[Dict[str, Union[str, int]]]]] = Field(
        None, description="Available facets for filtering"
    )

class SearchSuggestion(BaseModel):
    text: str = Field(..., description="Suggested search term")
    count: Optional[int] = Field(None, ge=0, description="Number of results for this suggestion")
    type: Optional[ContentType] = Field(None, description="Primary content type for this suggestion")

class SearchSuggestionsResponse(BaseModel):
    suggestions: List[SearchSuggestion] = Field(description="Search suggestions")
    query: str = Field(description="Original partial query")

class SearchStats(BaseModel):
    total_searchable_content: int = Field(ge=0, description="Total searchable items")
    content_types: Dict[str, int] = Field(description="Count by content type")
    popular_searches: Optional[List[str]] = Field(None, description="Most popular search terms")
    last_indexed: Optional[datetime] = Field(None, description="When search index was last updated")
    search_enabled: bool = Field(True, description="Whether search is currently enabled")

# Error response schemas
class SearchError(BaseModel):
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

# Utility function to convert generic results to specific types
def create_specialized_result(result: SearchResult) -> Union[AlbumSearchResult, ImageSearchResult, UploadSearchResult, CommentSearchResult, UserSearchResult, PageSearchResult, SearchResult]:
    """Convert a generic SearchResult to a specialized type based on content type."""
    try:
        if result.type == ContentType.ALBUM:
            return AlbumSearchResult(**result.dict())
        elif result.type == ContentType.IMAGE:
            return ImageSearchResult(**result.dict())
        elif result.type == ContentType.UPLOAD:
            return UploadSearchResult(**result.dict())
        elif result.type == ContentType.COMMENT:
            return CommentSearchResult(**result.dict())
        elif result.type == ContentType.USER:
            return UserSearchResult(**result.dict())
        elif result.type == ContentType.PAGE:
            return PageSearchResult(**result.dict())
        else:
            return result
    except Exception:
        # Fallback to generic result if conversion fails
        return result
