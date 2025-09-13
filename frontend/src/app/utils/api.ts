const API = "http://localhost:8000";

export async function fetchImages(skip = 0, limit = 100) {
  const res = await fetch(`${API}/images/images/?skip=${skip}&limit=${limit}`);
  return res.json();
}

export async function fetchImageComments(imageId: string) {
  const res = await fetch(`${API}/comments/images/${imageId}`);
  return res.json();
}

export async function postImageComment(imageId: string, content: string, token: string) {
  const res = await fetch(`${API}/comments/images/${imageId}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  return res.json();
}

export async function toggleLike(imageId: string, token: string) {
  const res = await fetch(`${API}/likes/toggle`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: imageId }),
  });
  return res.json();
}

// Albums
export async function fetchAlbums() {
  const res = await fetch(`${API}/albums/albums/`);
  return res.json();
}

// Users
export async function fetchUsers() {
  const res = await fetch(`${API}/users/`);
  return res.json();
}

// Uploads
export async function fetchUploads() {
  const res = await fetch(`${API}/uploads/`);
  return res.json();
}

// Search
export async function searchImages(query: string) {
  const res = await fetch(`${API}/search/images?query=${encodeURIComponent(query)}`);
  return res.json();
}
