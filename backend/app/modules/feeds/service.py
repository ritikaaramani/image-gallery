from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.modules.images import models as image_models
from app.modules.albums import models as album_models
from typing import Literal

def generate_rss(db: Session, content_type: Literal["images", "albums"] = "images"):
    """
    Generates an RSS feed for either images or albums.
    """
    if content_type == "albums":
        items = db.query(album_models.Album).order_by(album_models.Album.created_at.desc()).limit(20).all()
        item_list = ""
        for item in items:
            item_list += f"""
            <item>
                <title>{item.title}</title>
                <link>/albums/{item.id}</link>
                <description>{item.description or ''}</description>
                <pubDate>{item.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
            </item>
            """
    else:  # Default to images
        items = db.query(image_models.Image).order_by(image_models.Image.created_at.desc()).limit(20).all()
        item_list = ""
        for item in items:
            item_list += f"""
            <item>
                <title>{item.title}</title>
                <link>/images/{item.id}</link>
                <description>{item.description or ''}</description>
                <pubDate>{item.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
            </item>
            """

    rss = f"""<?xml version="1.0"?>
    <rss version="2.0">
        <channel>
            <title>My Blog Feed</title>
            <link>/</link>
            <description>Latest {content_type.capitalize()}</description>
            {item_list}
        </channel>
    </rss>"""
    return Response(content=rss, media_type="application/rss+xml")

def generate_atom(db: Session, content_type: Literal["images", "albums"] = "images"):
    """
    Generates an Atom feed for either images or albums.
    """
    if content_type == "albums":
        items = db.query(album_models.Album).order_by(album_models.Album.created_at.desc()).limit(20).all()
    else:  # Default to images
        items = db.query(image_models.Image).order_by(image_models.Image.created_at.desc()).limit(20).all()
    
    entries = ""
    for item in items:
        entries += f"""
        <entry>
            <title>{item.title}</title>
            <link href="/{content_type}/{item.id}"/>
            <summary>{item.description or ''}</summary>
            <updated>{item.created_at.isoformat()}</updated>
            <id>tag:myblog,{item.id}</id>
        </entry>
        """

    atom = f"""<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <title>My Blog Feed</title>
        <link href="/"/>
        <updated>{items[0].created_at.isoformat() if items else ''}</updated>
        <id>tag:myblog,feed</id>
        {entries}
    </feed>"""
    return Response(content=atom, media_type="application/atom+xml")
