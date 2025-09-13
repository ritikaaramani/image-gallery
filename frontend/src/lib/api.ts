// src/lib/api.ts
export const API = process.env.NEXT_PUBLIC_API_URL;

export async function fetchUploads() {
  const res = await fetch(`${API}/uploads`);
  if (!res.ok) throw new Error("Failed to fetch uploads");
  return res.json();
}
