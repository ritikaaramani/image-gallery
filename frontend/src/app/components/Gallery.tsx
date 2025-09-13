"use client";

import { useEffect, useRef, useState } from "react";
import Image from 'next/image';

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Comment {
  id: string;
  text: string;
  user: string;
}

interface Image {
  id: string;
  url: string;
  title: string;
  likes: number;
  views: number;
  comments: Comment[];
  is_liked?: boolean;
  description?: string;
  created_at?: string;
  user?: string;
}

interface Album {
  id: string;
  title: string;
  description: string;
  image_count: number;
  cover_image?: string;
  created_at: string;
  user?: string;
}

interface Upload {
  id: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_date: string;
  status: string;
}

interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  image_count?: number;
}

type ViewMode = 'images' | 'albums' | 'uploads' | 'users';

export default function Gallery() {
  const [images, setImages] = useState<Image[]>([]);
  const [albums, setAlbums] = useState<Album[]>([]);
  const [selectedAlbum, setSelectedAlbum] = useState<Album | null>(null);
  const [albumImages, setAlbumImages] = useState<Image[]>([]);
  const [isLoadingAlbum, setIsLoadingAlbum] = useState(false);
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userMap, setUserMap] = useState<Record<string, string>>({});
  const [viewMode, setViewMode] = useState<ViewMode>('images');
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [showCreateAlbum, setShowCreateAlbum] = useState(false);
  const [showAddImageToAlbum, setShowAddImageToAlbum] = useState(false);
  const [albumAddQuery, setAlbumAddQuery] = useState('');
  const [albumAddResults, setAlbumAddResults] = useState<Image[]>([]);
  const [showRegister, setShowRegister] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [capA, setCapA] = useState<number>(() => Math.floor(Math.random() * 10) + 1);
  const [capB, setCapB] = useState<number>(() => Math.floor(Math.random() * 10) + 1);
  const [capResp, setCapResp] = useState('');
  const [droppedFile, setDroppedFile] = useState<File | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const observedMapRef = useRef<Map<string, Element>>(new Map());
  const viewedIdsRef = useRef<Set<string>>(new Set());
  
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    setToken(storedToken);
    try {
      const storedViewed = sessionStorage.getItem('viewedImageIds');
      if (storedViewed) viewedIdsRef.current = new Set(JSON.parse(storedViewed));
    } catch {}
  }, []);

  const decodeJwt = (jwt: string): any | null => {
    try {
      const parts = jwt.split('.');
      if (parts.length < 2) return null;
      const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
      return payload || null;
    } catch { return null; }
  };

  useEffect(() => {
    const initCurrentUser = async () => {
      if (!token) { setCurrentUser(null); return; }
      const payload = decodeJwt(token);
      const userId = payload?.sub;
      if (!userId) { setCurrentUser(null); return; }
      try {
        const res = await fetch(`${API}/users/${userId}`, { cache: 'no-store' });
        if (res.ok) {
          const data = await res.json();
          setCurrentUser(data);
        }
      } catch {}
    };
    initCurrentUser();
  }, [token]);

  const persistViewed = () => {
    try { sessionStorage.setItem('viewedImageIds', JSON.stringify(Array.from(viewedIdsRef.current))); } catch {}
  };

  const incrementView = async (imageId: string) => {
    if (!imageId || viewedIdsRef.current.has(imageId)) return;
    viewedIdsRef.current.add(imageId);
    persistViewed();
    setImages(prev => prev.map(img => img.id === imageId ? { ...img, views: (img.views || 0) + 1 } : img));
    setAlbumImages(prev => prev.map(img => img.id === imageId ? { ...img, views: (img.views || 0) + 1 } : img));
    try {
      // Optional backend ping if supported; safe to ignore failures
      await fetch(`${API}/images/${imageId}/view`, { method: 'POST', cache: 'no-store' });
    } catch {}
  };

  useEffect(() => {
    if (observerRef.current) observerRef.current.disconnect();
    observerRef.current = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const target = entry.target as HTMLElement;
        const id = target.getAttribute('data-image-id') || '';
        if (entry.isIntersecting && id) {
          incrementView(id);
          const obs = observerRef.current;
          if (obs) obs.unobserve(target);
          observedMapRef.current.delete(id);
        }
      });
    }, { threshold: 0.5 });

    // Reconnect existing observed elements after observer recreation
    observedMapRef.current.forEach((el) => {
      observerRef.current?.observe(el);
    });

    return () => observerRef.current?.disconnect();
  }, []);

  const registerImageElement = (id: string) => (el: Element | null) => {
    if (!el || !observerRef.current) return;
    // If already viewed, skip observing
    if (viewedIdsRef.current.has(id)) return;
    el.setAttribute('data-image-id', id);
    observerRef.current.observe(el);
    observedMapRef.current.set(id, el);
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API}/users`);
      const data = await res.json();
      const map: Record<string, string> = {};
      data.forEach((u: any) => (map[u.id] = u.username));
      setUserMap(map);
      setUsers(data);
    } catch (err) {
      console.error("Error fetching users:", err);
    }
  };

  const fetchGallery = async () => {
    try {
      const res = await fetch(`${API}/gallery?ts=${Date.now()}`, { cache: 'no-store' });
      const data = await res.json();

      const imagesWithComments = await Promise.all(
        Array.isArray(data) ? data.map(async (img: any) => {
          try {
            const commentsRes = await fetch(`${API}/comments/images/${img.id}?ts=${Date.now()}`, { cache: 'no-store' });
            const commentsData = await commentsRes.json();
            const mappedComments: Comment[] = Array.isArray(commentsData) 
              ? commentsData.map((c: any) => ({
                  id: c.id,
                  text: c.content,
                  user: c.user_id && userMap[c.user_id] ? userMap[c.user_id] : "Anonymous",
                }))
              : [];
            
            let isLiked = false;
            if (token) {
              try {
                const likeRes = await fetch(`${API}/likes/check/${img.id}?ts=${Date.now()}`, {
                  headers: { Authorization: `Bearer ${token}` },
                  cache: 'no-store'
                });
                if (likeRes.ok) {
                  const likeData = await likeRes.json();
                  isLiked = likeData.is_liked || false;
                }
              } catch (err) {
                console.error("Failed to fetch like status for image", img.id, err);
              }
            }
            
            const imageUrl = img.url.includes("/uploads/files/")
              ? img.url.replace("/uploads/files/", "/static/uploads/")
              : img.url;

            return { 
              ...img, 
              url: imageUrl,
              comments: mappedComments, 
              is_liked: isLiked,
              likes: img.likes || 0,
              views: img.views || 0
            };
          } catch (err) {
            console.error("Failed to fetch comments for image", img.id, err);
            const fallbackUrl = img.url.includes("/uploads/files/")
              ? img.url.replace("/uploads/files/", "/static/uploads/")
              : img.url;

            return { 
              ...img, 
              url: fallbackUrl,
              comments: [], 
              is_liked: false,
              likes: img.likes || 0,
              views: img.views || 0
            };
          }
        }) : []
      );

      setImages(imagesWithComments);
    } catch (err) {
      console.error("Error fetching gallery:", err);
    }
  };

  const refreshGallery = async () => {
    console.log('Manual gallery refresh triggered');
    await fetchGallery();
  };

  const fetchAlbums = async () => {
    try {
      const res = await fetch(`${API}/albums?ts=${Date.now()}`, { cache: 'no-store' });
      const data = await res.json();
      setAlbums(data);
    } catch (err) {
      console.error("Error fetching albums:", err);
    }
  };

  const fetchAlbumImages = async (albumId: string) => {
    setIsLoadingAlbum(true);

    const filterByAlbum = (imgs: any[], albumIdVal: string): any[] => {
      return imgs.filter((img: any) => {
        if (img == null) return false;
        if (img.album_id && img.album_id === albumIdVal) return true;
        if (img.albumId && img.albumId === albumIdVal) return true;
        if (Array.isArray(img.albums)) {
          return img.albums.some((a: any) => a && (a.id === albumIdVal || a.album_id === albumIdVal));
        }
        return false;
      });
    };

    const formatAndEnrich = async (imgs: any[]): Promise<Image[]> => {
      return Promise.all(
        imgs.map(async (img: any) => {
          try {
            // Comments
            const commentsRes = await fetch(`${API}/comments/images/${img.id}`);
            const commentsData = await commentsRes.json();
            const mappedComments: Comment[] = Array.isArray(commentsData)
              ? commentsData.map((c: any) => ({
                  id: c.id,
                  text: c.content,
                  user: c.user_id && userMap[c.user_id] ? userMap[c.user_id] : 'Anonymous',
                }))
              : [];

            // Like status
            let isLiked = false;
            if (token) {
              try {
                const likeRes = await fetch(`${API}/likes/check/${img.id}`, {
                  headers: { Authorization: `Bearer ${token}` },
                });
                if (likeRes.ok) {
                  const likeData = await likeRes.json();
                  isLiked = likeData.is_liked || false;
                }
              } catch (err) {
                console.error('Failed to fetch like status for image', img.id, err);
              }
            }

            // Build a robust image URL similar to the Images tab handling
            const rawUrl = img.url || img.file_url || img.path || '';
            let imageUrl = rawUrl;
            if (rawUrl.includes('/uploads/files/')) {
              imageUrl = rawUrl.replace('/uploads/files/', '/static/uploads/');
            } else if (!rawUrl && (img.filename || img.id)) {
              // Backend stores files at /static/uploads/<uuid>
              imageUrl = `${API}/static/uploads/${img.filename || img.id}`;
            }

            return {
              ...img,
              id: img.id,
              url: imageUrl,
              title: img.title || 'Untitled',
              comments: mappedComments,
              is_liked: isLiked,
              likes: img.likes || 0,
              views: img.views || 0,
              description: img.caption || img.description || '',
              created_at: img.created_at || new Date().toISOString(),
              user: img.user || '',
            } as Image;
          } catch (err) {
            console.error('Failed to enrich album image', img.id, err);
            const rawUrl = img.url || img.file_url || img.path || '';
            let fallbackUrl = rawUrl;
            if (rawUrl.includes('/uploads/files/')) {
              fallbackUrl = rawUrl.replace('/uploads/files/', '/static/uploads/');
            } else if (!rawUrl && (img.filename || img.id)) {
              fallbackUrl = `${API}/static/uploads/${img.filename || img.id}`;
            }

            return {
              ...img,
              id: img.id,
              url: fallbackUrl,
              comments: [],
              is_liked: false,
              likes: img.likes || 0,
              views: img.views || 0,
              title: img.title || 'Untitled',
              description: img.caption || img.description || '',
              created_at: img.created_at || new Date().toISOString(),
              user: img.user || '',
            } as Image;
          }
        })
      );
    };

    try {
      // 1) Album detail that may embed images
      const url2 = `${API}/albums/${albumId}`;
      try {
        const res2 = await fetch(url2, token ? { headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' } : { cache: 'no-store' });
        if (res2.ok) {
          const data2 = await res2.json();
          if (Array.isArray(data2?.images)) {
            const imagesArray = data2.images;
            const filtered2 = filterByAlbum(imagesArray, albumId);
            setAlbumImages(await formatAndEnrich(filtered2));
            return;
          }
        }
      } catch {}

      // 2) Query images by album_id
      const url3 = `${API}/images?album_id=${encodeURIComponent(albumId)}`;
      try {
        const res3 = await fetch(url3, token ? { headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' } : { cache: 'no-store' });
        if (res3.ok) {
          const data3 = await res3.json();
          if (Array.isArray(data3)) {
            // This endpoint should already be filtered, but enforce just in case
            const filtered3 = filterByAlbum(data3, albumId);
            setAlbumImages(await formatAndEnrich(filtered3));
            return;
          }
        }
      } catch {}

      // If all failed, show empty
      setAlbumImages([]);
    } catch (err) {
      console.error('Error fetching album images:', err);
      setAlbumImages([]);
    } finally {
      setIsLoadingAlbum(false);
    }
  };

  const fetchUploads = async () => {
    if (!token) return;
    try {
      const isAdmin = !!currentUser?.is_active && !!(currentUser as any)?.is_admin;
      const url = isAdmin ? `${API}/uploads?all=true` : `${API}/uploads/`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setUploads(data);
    } catch (err) {
      console.error("Error fetching uploads:", err);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    if (Object.keys(userMap).length > 0) {
      fetchGallery();
    }
  }, [userMap, token]);

  useEffect(() => {
    if (viewMode === 'albums') {
      fetchAlbums();
      setSelectedAlbum(null);
      setAlbumImages([]);
    }
    else if (viewMode === 'uploads') fetchUploads();
    else if (viewMode === 'users') fetchUsers();
  }, [viewMode, token, currentUser]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const res = await fetch(`${API}/search?q=${encodeURIComponent(searchQuery)}&type=${viewMode}`);
      const data = await res.json();
      
      if (viewMode === 'images') setImages(data);
      else if (viewMode === 'albums') setAlbums(data);
      else if (viewMode === 'uploads') setUploads(data);
      else if (viewMode === 'users') setUsers(data);
    } catch (err) {
      console.error("Search error:", err);
    }
  };

  const handleImageUpload = async (file: File, title: string, description: string) => {
    if (!token) {
      alert("You must be logged in to upload images.");
      return;
    }

    setIsUploading(true);
    
    try {
      const uploadFormData = new FormData();
      uploadFormData.append('file', file);
      if (description) uploadFormData.append('description', description);
      uploadFormData.append('privacy', 'public');
      
      const uploadRes = await fetch(`${API}/uploads/`, {
        method: 'POST',
        headers: {  
          'Authorization': `Bearer ${token}`
        },
        body: uploadFormData,
      });

      if (!uploadRes.ok) {
        let errorText = await uploadRes.text();
        throw new Error(`Upload failed (${uploadRes.status}): ${errorText}`);
      }
      
      const uploadData = await uploadRes.json();

      const imageFormData = new FormData();
      imageFormData.append('title', title);
      imageFormData.append('caption', description || '');
      imageFormData.append('privacy', 'public');
      imageFormData.append('license', '');
      imageFormData.append('upload_id', uploadData.id);

      const imageRes = await fetch(`${API}/images`, {
        method: 'POST',
        headers: {  
          'Authorization': `Bearer ${token}`
        },
        body: imageFormData,
      });

      if (!imageRes.ok) {
        let errorText = await imageRes.text();
        throw new Error(`Image creation failed (${imageRes.status}): ${errorText}`);
      }
      
      const newImage = await imageRes.json();
      
      const formattedNewImage: Image = {
        id: newImage.id,
        url: newImage.url || `${API}/static/uploads/${uploadData.filename}`,
        title: newImage.title || title,
        description: newImage.caption || description,
        likes: 0,
        views: 0,
        comments: [],
        is_liked: false,
        created_at: newImage.created_at || new Date().toISOString(),
        user: newImage.user || ''
      };
      
      setImages(prev => [formattedNewImage, ...prev]);
      setShowUploadForm(false);
      
      if (viewMode === 'uploads') {
        await fetchUploads();
      }
      
      alert("Image uploaded successfully!");
    } catch (err) {
      console.error("Upload error:", err);
      alert(`Upload failed: ${(err as Error).message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateAlbum = async (title: string, description: string) => {
    if (!token) return;

    try {
      const res = await fetch(`${API}/albums`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, description }),
      });

      if (!res.ok) throw new Error(await res.text());
      
      const newAlbum = await res.json();
      setAlbums(prev => [newAlbum, ...prev]);
      setShowCreateAlbum(false);
      alert("Album created successfully!");
    } catch (err) {
      console.error("Create album error:", err);
      alert((err as Error).message);
    }
  };

  const handleLike = async (id: string) => {
    if (!token) return alert("You must be logged in to like posts.");
    
    const currentImage = images.find(img => img.id === id);
    if (!currentImage) return;
    
    const previousLikedState = currentImage.is_liked;
    const previousLikesCount = currentImage.likes;
    
    setImages((prev) =>
      prev.map((img) =>
        img.id === id
          ? {
              ...img,
              likes: img.is_liked ? Math.max((img.likes || 1) - 1, 0) : (img.likes || 0) + 1,
              is_liked: !img.is_liked,
            }
          : img
      )
    );
    // Mirror optimistic like into album view if present
    setAlbumImages((prev) =>
      prev.map((img) =>
        img.id === id
          ? {
              ...img,
              likes: img.is_liked ? Math.max((img.likes || 1) - 1, 0) : (img.likes || 0) + 1,
              is_liked: !img.is_liked,
            }
          : img
      )
    );

    try {
      const res = await fetch(`${API}/likes/toggle?ts=${Date.now()}`, {
        method: "POST",
        headers: {  
          Authorization: `Bearer ${token}`,  
          "Content-Type": "application/json"  
        },
        cache: 'no-store',
        body: JSON.stringify({ image_id: id }),
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Like toggle failed: ${errorText}`);
      }
      
      const data = await res.json();
      
      setImages((prev) =>
        prev.map((img) =>
          img.id === id
            ? {
                ...img,
                likes: data.total_likes || data.likes || img.likes,
                is_liked: data.is_liked,
              }
            : img
        )
      );
      setAlbumImages((prev) =>
        prev.map((img) =>
          img.id === id
            ? {
                ...img,
                likes: data.total_likes || data.likes || img.likes,
                is_liked: data.is_liked,
              }
            : img
        )
      );
      
    } catch (err) {
      console.error("Like error:", err);
      
      setImages((prev) =>
        prev.map((img) =>
          img.id === id
            ? {
                ...img,
                likes: previousLikesCount,
                is_liked: previousLikedState,
              }
            : img
        )
      );
      setAlbumImages((prev) =>
        prev.map((img) =>
          img.id === id
            ? {
                ...img,
                likes: previousLikesCount,
                is_liked: previousLikedState,
              }
            : img
        )
      );
      
      alert(`Failed to update like: ${(err as Error).message}`);
    }
  };

  const handleComment = async (id: string, text: string) => {
    if (!token) return alert("You must be logged in to comment.");
    try {
      const res = await fetch(`${API}/comments/images/${id}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ content: text }),
      });
      if (!res.ok) throw new Error(await res.text());
      const newComment = await res.json();
      setImages((prev) =>
        prev.map((img) =>
          img.id === id
            ? {
                ...img,
                comments: [
                  ...img.comments,
                  {
                    id: newComment.id,
                    text: newComment.content,
                    user:
                      newComment.user_id && userMap[newComment.user_id]
                        ? userMap[newComment.user_id]
                        : "Anonymous",
                  },
                ],
              }
            : img
        )
      );
      // Mirror into album view
      setAlbumImages((prev) =>
        prev.map((img) =>
          img.id === id
            ? {
                ...img,
                comments: [
                  ...img.comments,
                  {
                    id: newComment.id,
                    text: newComment.content,
                    user:
                      newComment.user_id && userMap[newComment.user_id]
                        ? userMap[newComment.user_id]
                        : "Anonymous",
                  },
                ],
              }
            : img
        )
      );
    } catch (err) {
      console.error(err);
      alert((err as Error).message);
    }
  };

  const handleDeleteComment = async (imageId: string, commentId: string) => {
    if (!confirm('Delete this comment?')) return;
    if (!token) return alert("You must be logged in to delete comments.");
    try {
      const res = await fetch(`${API}/comments/${commentId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(await res.text());
      setImages(prev => prev.map(img => img.id === imageId ? { ...img, comments: img.comments.filter(c => c.id !== commentId) } : img));
      setAlbumImages(prev => prev.map(img => img.id === imageId ? { ...img, comments: img.comments.filter(c => c.id !== commentId) } : img));
    } catch (err) {
      console.error('Delete comment error:', err);
      alert((err as Error).message);
    }
  };

  const onDropFiles = (files: FileList | File[]) => {
    const arr = Array.from(files);
    const items = arr.map((f) => ({ id: crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${f.name}`, name: f.name, status: 'queued' as const, progress: 0 }));
    // setBatchItems(items); // Removed batchItems state
    // setBatchFiles(arr as File[]); // Removed batchFiles state
  };

  const startBatchUpload = async (files: File[]) => {
    if (!token) return alert('You must be logged in to upload images.');
    const arr: File[] = Array.from(files);
    for (let i = 0; i < arr.length; i++) {
      const file = arr[i];
      const itemId = 'batch-item-' + i; // Use a unique ID for each item
      // setBatchItems(prev => prev.map(b => b.id === itemId ? { ...b, status: 'uploading', progress: 10 } : b)); // Removed batchItems state
      try {
        const uploadFormData = new FormData();
        uploadFormData.append('file', file);
        uploadFormData.append('privacy', 'public');
        const uploadRes = await fetch(`${API}/uploads/`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: uploadFormData,
        });
        if (!uploadRes.ok) throw new Error(await uploadRes.text());
        const uploadData = await uploadRes.json();
        // setBatchItems(prev => prev.map(b => b.id === itemId ? { ...b, status: 'creating', progress: 60 } : b)); // Removed batchItems state

        const title = file.name.replace(/\.[^.]+$/, '');
        const imageFormData = new FormData();
        imageFormData.append('title', title);
        imageFormData.append('caption', '');
        imageFormData.append('privacy', 'public');
        imageFormData.append('license', '');
        imageFormData.append('upload_id', uploadData.id);
        const imageRes = await fetch(`${API}/images`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: imageFormData,
        });
        if (!imageRes.ok) throw new Error(await imageRes.text());
        const newImage = await imageRes.json();
        const formattedNewImage: Image = {
          id: newImage.id,
          url: newImage.url || `${API}/static/uploads/${uploadData.filename}`,
          title: newImage.title || title,
          description: newImage.caption || '',
          likes: 0,
          views: 0,
          comments: [],
          is_liked: false,
          created_at: newImage.created_at || new Date().toISOString(),
          user: newImage.user || ''
        };
        setImages(prev => [formattedNewImage, ...prev]);
        // setBatchItems(prev => prev.map(b => b.id === itemId ? { ...b, status: 'done', progress: 100 } : b)); // Removed batchItems state
      } catch (err) {
        console.error('Batch upload error:', err);
        // setBatchItems(prev => prev.map(b => b.id === itemId ? { ...b, status: 'error', error: (err as Error).message, progress: 100 } : b)); // Removed batchItems state
      }
    }
  };

  return (
    <div className="p-6 bg-[#ffece6ff] min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          
          {/* Search Bar */}
          <div className="flex items-center justify-center mb-6">
            <div className="flex w-full max-w-2xl">
              <input
                type="text"
                placeholder={`Search ${viewMode}...`}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-[#352828ff]"
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                onClick={handleSearch}
                className="px-6 py-2 bg-[#352828ff] text-white rounded-r-lg hover:bg-[#352828ff] transition-colors"
              >
                🔍 Search
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap justify-center gap-2 mb-6">
            {(['images', 'albums', 'uploads', 'users'] as ViewMode[])
              .filter((mode) => mode !== 'users' || (currentUser && (currentUser as any).is_admin))
              .map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  viewMode === mode
                    ? 'bg-[#352828ff] text-white'
                    : 'bg-white text-gray-700 hover:bg-[f6ebfaff]'
                }`}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>

          {/* Action Buttons */}
          {token && (
            <div className="flex justify-center gap-4 mb-6">
              {viewMode === 'images' && (
                <>
                  <button
                    onClick={() => setShowUploadForm(true)}
                    className="px-6 py-2 bg-[#bd9d9dff] text-white rounded-lg hover:bg-[#836868ff]transition-colors"
                  >
                    📤 Upload Image
                  </button>
                  <button
                    onClick={refreshGallery}
                    className="px-6 py-2 bg-[#352828ff] text-white rounded-lg hover:bg-[#352828ff] transition-colors"
                  >
                    🔄 Refresh Gallery
                  </button>
                </>
              )}
              {viewMode === 'albums' && (
                <div className="flex gap-4">
                <button
                  onClick={() => setShowCreateAlbum(true)}
                  className="px-6 py-2 bg-[#bd9d9dff] text-white rounded-lg hover:bg-[#352828ff] transition-colors"
                >
                  📁 Create Album
                  </button>
                  {selectedAlbum && (
                    <button
                      onClick={() => {
                        // Preload with existing images to ensure IDs match server
                        setAlbumAddResults(images);
                        setAlbumAddQuery('');
                        setShowAddImageToAlbum(true);
                      }}
                      className="px-6 py-2 bg-[#352828ff] text-white rounded-lg hover:bg-[#352828ff] transition-colors"
                    >
                      ➕ Add Image
                </button>
              )}
                </div>
              )}
            </div>
          )}
          {!token && (
            <div className="flex justify-center gap-4 mb-6">
              <button
                onClick={() => setShowRegister(true)}
                className="px-6 py-2 bg-[#352828ff] text-white rounded-lg hover:bg-[#352828ff] transition-colors"
              >
                Create Account
              </button>
            </div>
          )}
        </div>

        {/* Upload Form Modal */}
        {showUploadForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h3 className="text-xl font-semibold mb-4">Upload New Image</h3>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const form = e.target as HTMLFormElement;
                  const formData = new FormData(form);
                  const file = formData.get('file') as File;
                  const title = formData.get('title') as string;
                  const description = formData.get('description') as string;
                  const effectiveFile = droppedFile || file;
                  if (effectiveFile && title) {
                    handleImageUpload(effectiveFile, title, description);
                  } else {
                    alert('Please select or drop a file and provide a title.');
                  }
                }}
              >
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Select or Drop Image</label>
                  <div
                    onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                    onDrop={(e) => { e.preventDefault(); e.stopPropagation(); const f = e.dataTransfer.files?.[0]; if (f) setDroppedFile(f); }}
                    className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-2"
                  >
                    {droppedFile ? (
                      <span className="text-sm text-gray-700">Selected: {droppedFile.name}</span>
                    ) : (
                      <span className="text-sm text-gray-500">Drag and drop an image here</span>
                    )}
                  </div>
                  <input
                    type="file"
                    name="file"
                    accept="image/*"
                    className="w-full p-2 border rounded-lg"
                    onChange={(e) => { const f = e.target.files?.[0]; if (f) setDroppedFile(f); }}
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Title</label>
                  <input
                    type="text"
                    name="title"
                    required
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <textarea
                    name="description"
                    className="w-full p-2 border rounded-lg h-20"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={isUploading}
                    className="flex-1 bg-[#352828ff] text-white py-2 rounded-lg hover:bg-[#352828ff] disabled:opacity-50"
                  >
                    {isUploading ? 'Uploading...' : 'Upload'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowUploadForm(false)}
                    className="flex-1 bg-[f6ebfaff] text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Create Album Modal */}
        {showCreateAlbum && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h3 className="text-xl font-semibold mb-4">Create New Album</h3>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const form = e.target as HTMLFormElement;
                  const formData = new FormData(form);
                  const title = formData.get('title') as string;
                  const description = formData.get('description') as string;
                  
                  if (title) {
                    handleCreateAlbum(title, description);
                  }
                }}
              >
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Album Title</label>
                  <input
                    type="text"
                    name="title"
                    required
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <textarea
                    name="description"
                    className="w-full p-2 border rounded-lg h-20"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600"
                  >
                    Create Album
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateAlbum(false)}
                    className="flex-1 bg-[f6ebfaff] text-gray-700 py-2 rounded-lg hover:[f6ebfaff]"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Register Modal
        {showRegister && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h3 className="text-xl font-semibold mb-4">Create Account</h3>
              <form
                onSubmit={async (e) => {
                  e.preventDefault();
                  if (isRegistering) return;
                  const form = e.target as HTMLFormElement;
                  const formData = new FormData(form);
                  const username = String(formData.get('username') || '').trim();
                  const email = String(formData.get('email') || '').trim();
                  const password = String(formData.get('password') || '');
                  if (!username || !email || !password) {
                    alert('Please fill all fields.');
                    return;
                  }
                  if (Number(capResp) !== (capA + capB)) {
                    alert('Captcha incorrect.');
                    return;
                  }
                  setIsRegistering(true);
                  try {
                    // Register
                    const res = await fetch(`${API}/users/`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ 
                        username, 
                        email, 
                        password,
                        maptcha_response: Number(capResp),
                        maptcha_requested: capA + capB,
                        maptcha_challenge: `${capA}+${capB}`
                      })
                    });
                    if (!res.ok) {
                      const text = await res.text();
                      throw new Error(`Registration failed: ${text}`);
                    }
                    // Auto-login
                    const tokenRes = await fetch(`${API}/users/token`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                      body: new URLSearchParams({ username, password })
                    });
                    if (tokenRes.ok) {
                      const t = await tokenRes.json();
                      if (t?.access_token) {
                        localStorage.setItem('token', t.access_token);
                        setToken(t.access_token);
                        setShowRegister(false);
                        alert('Account created and logged in.');
                      } else {
                        alert('Account created. Please log in.');
                        setShowRegister(false);
                      }
                    } else {
                      alert('Account created. Please log in.');
                      setShowRegister(false);
                    }
                  } catch (err) {
                    console.error(err);
                    alert((err as Error).message);
                  } finally {
                    setIsRegistering(false);
                  }
                }}
              >
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Username</label>
                  <input name="username" type="text" required className="w-full p-2 border rounded-lg" />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <input name="email" type="email" required className="w-full p-2 border rounded-lg" />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium mb-2">Password</label>
                  <input name="password" type="password" required minLength={6} className="w-full p-2 border rounded-lg" />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium mb-2">Captcha: What is {capA} + {capB}?</label>
                  <input 
                    type="number" 
                    value={capResp} 
                    onChange={(e) => setCapResp(e.target.value)} 
                    required
                    className="w-full p-2 border rounded-lg" />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={isRegistering}
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isRegistering ? 'Creating...' : 'Create Account'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowRegister(false)}
                    className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        */}
        {/* Batch uploader removed per requirements */}

        {/* Add Image To Album Modal */}
        {showAddImageToAlbum && selectedAlbum && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
              <h3 className="text-xl font-semibold mb-4">Add Image to "{selectedAlbum.title}"</h3>
              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={albumAddQuery}
                  onChange={(e) => setAlbumAddQuery(e.target.value)}
                  placeholder="Search your images by title..."
                  className="flex-1 p-2 border rounded-lg"
                />
                <button
                  onClick={() => {
                    const q = albumAddQuery.trim().toLowerCase();
                    if (!q) {
                      setAlbumAddResults(images);
                      return;
                    }
                    setAlbumAddResults(
                      images.filter((img) => (img.title || '').toLowerCase().includes(q))
                    );
                  }}
                  className="px-4 py-2 bg-grey-500 text-white rounded-lg hover:bg-grey-600"
                >
                  Filter
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-h-80 overflow-auto mb-4">
                {albumAddResults.map((img) => (
                  <div key={img.id} className="border rounded-lg overflow-hidden">
                    {/* Image wrapper for fill */}
                    <div className="relative w-full h-28">
                      <Image
                        src={img.url}
                        alt={img.title}
                        fill
                        className="object-cover"
                        onError={(e) => {
                        console.error('Failed to load image:', img.url);
                        e.currentTarget.src =
                        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y3ZjdmNyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjYWFhIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+PC9zdmc+';
                      }}
                        onLoad={() => {
                          console.log('Image loaded successfully:', img.url);
                        }}
                      />
                    </div>
                    <div className="p-2 flex items-center justify-between text-sm">
                      <span className="truncate mr-2">{img.title}</span>
                      <button
                        className="px-2 py-1 bg-[#352828ff] text-white rounded hover:bg-[#352828ff]"
                        onClick={async () => {
                          if (!token) return alert('Login required');
                          try {
                            const res = await fetch(`${API}/albums/${selectedAlbum.id}/images/${img.id}`, {
                              method: 'POST',
                              headers: { 'Authorization': `Bearer ${token}` }
                            });
                            if (!res.ok) throw new Error(await res.text());
                            // Optimistically insert into album grid using the same formatting as gallery
                            setAlbumImages((prev) => [
                              {
                                id: img.id,
                                url: img.url,
                                title: img.title || 'Untitled',
                                likes: img.likes || 0,
                                views: img.views || 0,
                                comments: img.comments || [],
                                is_liked: img.is_liked || false,
                                description: img.description || '',
                                created_at: img.created_at || new Date().toISOString(),
                                user: img.user || ''
                              },
                              ...prev
                            ]);
                            // Optimistically bump count in UI
                            setSelectedAlbum((prev) => prev ? { ...prev, image_count: (prev.image_count || 0) + 1 } : prev);
                            alert('Image added to album');
                          } catch (err) {
                            console.error('Add image to album failed', err);
                            alert((err as Error).message);
                          }
                        }}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                ))}
                {albumAddResults.length === 0 && (
                  <div className="text-gray-500 col-span-full text-center space-y-2">
                    <p>No images found. Try clearing the filter.</p>
                    {images.length === 0 && (
                      <button
                        onClick={async () => {
                          await fetchGallery();
                          setAlbumAddResults(images);
                        }}
                        className="px-3 py-1 bg-[f6ebfaff] rounded hover:bg-[f6ebfaff]"
                      >
                        Load Images
                      </button>
                    )}
                  </div>
                )}
              </div>

              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setShowAddImageToAlbum(false)}
                  className="px-4 py-2 bg-[f6ebfaff] text-gray-700 rounded-lg hover:bg-[f6ebfaff]"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Content Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {/* Images View */}
          {viewMode === 'images' && images.length === 0 && (
            <p className="text-center col-span-full text-gray-500">No images yet.</p>
          )}

          {viewMode === 'images' && images.map((image) => {
            // Safe destructuring with defaults
            const {
              id = '',
              url = '',
              title = 'Untitled',
              likes = 0,
              views = 0,
              comments = [],
              is_liked = false,
              description = '',
              created_at = '',
              user = ''
            } = image || {};

            return (
              <div
                key={id}
                className="bg-[#f6ebfaff] rounded-2xl shadow-md overflow-hidden flex flex-col transition-transform transform hover:scale-105"
              >
                <div className="relative w-full h-40 rounded-t-xl overflow-hidden">
                  <Image
                    ref={registerImageElement(id)}
                    src={url}
                    alt={title}
                    fill
                    className="object-cover"
                    onError={(e) => {
                    console.error('Failed to load image:', url);
                    e.currentTarget.src =
                      'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y3ZjdmNyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjYWFhIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+PC9zdmc+';
                    }}
                    onLoad={() => {
                      console.log('Image loaded successfully:', url);
                    }}
                />
                </div>

                <div className="p-4 flex-1 flex flex-col justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-grey-800 mb-2 truncate">{title}</h3>
                    {description && (
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">{description}</p>
                    )}

                    <div className="flex items-center text-gray-500 text-sm mb-2 gap-4">
                      <button
                        onClick={() => handleLike(id)}
                        className={`flex items-center gap-1 transition ${
                          is_liked ? "text-red-500" : ""
                        }`}
                      >
                        ❤️ {likes}
                      </button>
                      <span>👀 {views} views</span>
                      {token && (
                        <button
                          className="bg-red-100 text-red-700 px-3 rounded-r text-sm hover:bg-red-200 transition-colors ml-2"
                          onClick={async () => {
                            if (!confirm('Delete this image?')) return;
                            try {
                              const res = await fetch(`${API}/images/${id}`, { method: 'DELETE', headers: token ? { Authorization: `Bearer ${token}` } : undefined });
                              if (!res.ok) throw new Error(await res.text());
                              setImages(prev => prev.filter(img => img.id !== id));
                              setAlbumImages(prev => prev.filter(img => img.id !== id));
                            } catch (err) {
                              alert((err as Error).message);
                            }
                          }}
                        >
                          🗑️
                        </button>
                      )}
                    </div>

                    <div className="text-sm text-gray-600 flex-1 overflow-y-auto max-h-32">
                      <h4 className="font-medium mb-1">Comments</h4>
                      {Array.isArray(comments) && comments.length > 0 ? (
                        comments.map((c) => (
                          <div key={c.id} className="mb-1 flex items-center gap-2">
                            <p className="flex-1">
                            <span className="font-semibold">{c.user}:</span> {c.text}
                          </p>
                            {token && (
                              <button
                                className="text-xs text-red-600 hover:text-red-700"
                                onClick={() => handleDeleteComment(id, c.id)}
                              >
                                Delete
                              </button>
                            )}
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-400">No comments yet.</p>
                      )}
                    </div>
                  </div>

                  {token && (
                    <div className="mt-3 flex">
                      <input
                        id={`comment-${id}`}
                        type="text"
                        placeholder="Add a comment..."
                        className="flex-1 border rounded-l px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-[#352828ff]"
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            const text = (e.target as HTMLInputElement).value;
                            if (!text.trim()) return;
                            handleComment(id, text);
                            (e.target as HTMLInputElement).value = "";
                          }
                        }}
                      />
                      <button
                        className="bg-[#352828ff] text-white px-4 rounded-r text-sm hover:bg-[#352828ff] transition-colors"
                        onClick={() => {
                          const input = document.querySelector<HTMLInputElement>(
                            `#comment-${id}`
                          );
                          if (input && input.value.trim()) {
                            handleComment(id, input.value);
                            input.value = "";
                          }
                        }}
                      >
                        Post
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Albums View */}
          {viewMode === 'albums' && !selectedAlbum && albums.length === 0 && (
            <p className="text-center col-span-full text-gray-500">No albums yet.</p>
          )}

          {viewMode === 'albums' && !selectedAlbum && albums.map((album) => (
            <button
              key={album.id}
              onClick={() => {
                setSelectedAlbum(album);
                fetchAlbumImages(album.id);
              }}
              className="text-left bg-[#f6ebfaff] rounded-2xl shadow-md overflow-hidden hover:shadow-lg transition-shadow"
            >
              {album.cover_image && album.cover_image.trim() !== '' ? (
                <div className="w-full h-40 relative">
                  <Image src={album.cover_image} alt={album.title} fill className="object-cover rounded-md" />
                </div>

              ) : (
                <div className="w-full h-40 bg-[f6ebfaff] flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <div className="text-4xl mb-2">📁</div>
                    <div className="text-sm">Album Cover</div>
                  </div>
                </div>
              )}
              <div className="p-4">
                <h3 className="text-lg font-semibold mb-2">{album.title}</h3>
                <p className="text-gray-600 text-sm mb-2">{album.description}</p>
                <div className="flex justify-between text-sm text-gray-500">
                  <span>📸 {album.image_count} images</span>
                  <div className="flex items-center gap-3">
                  <span>{new Date(album.created_at).toLocaleDateString()}</span>
                    {token && (
                      <button
                        className="text-red-600 hover:text-red-700"
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (!confirm('Delete this album?')) return;
                          try {
                            const res = await fetch(`${API}/albums/${album.id}`, {
                              method: 'DELETE',
                              headers: { Authorization: `Bearer ${token}` }
                            });
                            if (!res.ok) throw new Error(await res.text());
                            setAlbums(prev => prev.filter(a => a.id !== album.id));
                          } catch (err) {
                            alert((err as Error).message);
                          }
                        }}
                      >
                        Delete
                      </button>
                    )}
                </div>
              </div>
            </div>
            </button>
          ))}

          {viewMode === 'albums' && selectedAlbum && (
            <>
              <div className="col-span-full flex items-center justify-between mb-2">
                <div>
                  <button
                    onClick={() => {
                      setSelectedAlbum(null);
                      setAlbumImages([]);
                    }}
                    className="mr-2 px-3 py-1 rounded [f6ebfaff] hover:[f6ebfaff]"
                  >
                    ← Back to Albums
                  </button>
                  <span className="font-semibold">{selectedAlbum.title}</span>
                </div>
                <span className="text-sm text-gray-500">{selectedAlbum.description}</span>
              </div>

              {isLoadingAlbum && (
                <p className="text-center col-span-full text-gray-500">Loading images…</p>
              )}

              {!isLoadingAlbum && albumImages.length === 0 && (
                <p className="text-center col-span-full text-gray-500">No images in this album yet.</p>
              )}

              {!isLoadingAlbum && albumImages.map((image) => {
                const {
                  id = '',
                  url = '',
                  title = 'Untitled',
                  likes = 0,
                  views = 0,
                  comments = [],
                  is_liked = false,
                  description = '',
                  created_at = '',
                  user = ''
                } = image || {};

                return (
                  <div
                    key={id}
                    className="bg-[#f6ebfaff] rounded-2xl shadow-md overflow-hidden flex flex-col transition-transform transform hover:scale-105"
                  >
                    {url ? (
                      <div className="w-full h-40 relative">
                        <Image ref={registerImageElement(id)} src={url} alt={title} className="object-cover" onError={(e) => { console.error('Failed to load image:', url); e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y3ZjdmNyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjYWFhIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+PC9zdmc+'; }} onLoad={() => { console.log('Image loaded successfully:', url); }} fill />
                      </div>

                    ) : (
                      <div className="w-full h-40 [f6ebfaff] flex items-center justify-center text-gray-500">No image</div>
                    )}

                    <div className="p-4 flex-1 flex flex-col justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800 mb-2 truncate">{title}</h3>
                        {description && (
                          <p className="text-sm text-gray-600 mb-2 line-clamp-2">{description}</p>
                        )}

                        <div className="flex items-center text-gray-500 text-sm mb-2 gap-4">
                          <button
                            onClick={() => handleLike(id)}
                            className={`flex items-center gap-1 transition ${
                              is_liked ? "text-red-500" : ""
                            }`}
                          >
                            ❤️ {likes}
                          </button>
                          <span>👀 {views} views</span>
                          {selectedAlbum && token && (
                            <button
                              onClick={async () => {
                                try {
                                  const res = await fetch(`${API}/albums/${selectedAlbum.id}/images/${id}`, {
                                    method: 'DELETE',
                                    headers: { 'Authorization': `Bearer ${token}` }
                                  });
                                  if (!res.ok) throw new Error(await res.text());
                                  setAlbumImages(prev => prev.filter(img => img.id !== id));
                                  setSelectedAlbum((prev) => prev ? { ...prev, image_count: Math.max((prev.image_count || 1) - 1, 0) } : prev);
                                  alert('Image removed from album');
                                } catch (err) {
                                  console.error('Remove image from album failed', err);
                                  alert((err as Error).message);
                                }
                              }}
                              className="ml-auto text-red-600 hover:text-red-700"
                              title="Remove from album"
                            >
                              Remove
                            </button>
                          )}
                        </div>

                        <div className="text-sm text-gray-600 flex-1 overflow-y-auto max-h-32">
                          <h4 className="font-medium mb-1">Comments</h4>
                          {Array.isArray(comments) && comments.length > 0 ? (
                            comments.map((c) => (
                              <div key={c.id} className="mb-1 flex items-center gap-2">
                                <p className="flex-1">
                                  <span className="font-semibold">{c.user}:</span> {c.text}
                                </p>
                                {token && (
                                  <button
                                    className="text-xs text-red-600 hover:text-red-700"
                                    onClick={() => handleDeleteComment(id, c.id)}
                                  >
                                    Delete
                                  </button>
                                )}
                              </div>
                            ))
                          ) : (
                            <p className="text-gray-400">No comments yet.</p>
                          )}
                        </div>
                      </div>

                      {token && (
                        <div className="mt-3 flex">
                          <input
                            id={`album-comment-${id}`}
                            type="text"
                            placeholder="Add a comment..."
                            className="flex-1 border rounded-l px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-[#352828ff]"
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                const text = (e.target as HTMLInputElement).value;
                                if (!text.trim()) return;
                                handleComment(id, text);
                                (e.target as HTMLInputElement).value = "";
                              }
                            }}
                          />
                          <button
                            className="bg-[#352828ff] text-white px-4 rounded-r text-sm hover:bg-[#352828ff] transition-colors"
                            onClick={() => {
                              const input = document.querySelector<HTMLInputElement>(
                                `#album-comment-${id}`
                              );
                              if (input && input.value.trim()) {
                                handleComment(id, input.value);
                                input.value = "";
                              }
                            }}
                          >
                            Post
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </>
          )}

          {/* Uploads View */}
          {viewMode === 'uploads' && uploads.length === 0 && (
            <p className="text-center col-span-full text-gray-500">No uploads yet.</p>
          )}

          {viewMode === 'uploads' && uploads.map((upload) => (
            <div key={upload.id} className="bg-white rounded-2xl shadow-md p-4">
              <h3 className="font-semibold mb-2 truncate">{upload.filename}</h3>
              <div className="text-sm text-gray-600 space-y-1">
                <p>Type: {upload.file_type}</p>
                <p>Size: {(upload.file_size / 1024 / 1024).toFixed(2)} MB</p>
                <p>Status: <span className={upload.status === 'completed' ? 'text-[#352828ff]' : 'text-yellow-600'}>{upload.status}</span></p>
                <p>Uploaded: {new Date(upload.upload_date).toLocaleDateString()}</p>
              </div>
            </div>
          ))}

          {/* Users View */}
          {viewMode === 'users' && users.length === 0 && (
            <p className="text-center col-span-full text-gray-500">No users yet.</p>
          )}

          {viewMode === 'users' && users.map((user) => (
            <div key={user.id} className="bg-white rounded-2xl shadow-md p-4">
              <h3 className="font-semibold mb-2">{user.username}</h3>
              <div className="text-sm text-gray-600 space-y-1">
                <p>Email: {user.email}</p>
                <p>Images: {user.image_count || 0}</p>
                <p>Joined: {new Date(user.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}