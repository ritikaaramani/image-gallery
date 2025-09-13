"use client";

import { useState } from "react";

interface Comment {
  id: string;
  text: string;
  user: string;
}

interface ImageCardProps {
  id: string;
  url: string;
  title: string;
  likes: number;
  views: number;
  comments: Comment[];
  is_liked?: boolean;
  token?: string | null;
  onLike: (id: string) => void;
  onComment: (id: string, text: string) => void;
}

export default function ImageCard({
  id,
  url,
  title,
  likes,
  views,
  comments,
  is_liked,
  token,
  onLike,
  onComment,
}: ImageCardProps) {
  return (
    <div className="bg-[#ffece6ff] rounded-2xl shadow-md overflow-hidden flex flex-col transition-transform transform hover:scale-105">
      <img src={url} alt={title} className="w-full h-40 object-cover" />

      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2 truncate">{title}</h3>

          <div className="flex items-center text-gray-500 text-sm mb-2 gap-4">
            <button
              onClick={() => onLike(id)}
              className={`flex items-center gap-1 transition ${is_liked ? "text-red-500" : ""}`}
            >
              ❤️ {likes}
            </button>
            <span>👀 {views} views</span>
          </div>

          <div className="text-sm text-gray-600 flex-1 overflow-y-auto max-h-32">
            <h4 className="font-medium mb-1">Comments</h4>
            {comments.length > 0 ? (
              comments.map((c) => (
                <p key={c.id} className="mb-1">
                  <span className="font-semibold">{c.user}:</span> {c.text}
                </p>
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
              className="flex-1 border rounded-l px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-400"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  const text = (e.target as HTMLInputElement).value;
                  if (!text.trim()) return;
                  onComment(id, text);
                  (e.target as HTMLInputElement).value = "";
                }
              }}
            />
            <button
              className="bg-blue-500 text-white px-4 rounded-r text-sm hover:bg-blue-600 transition-colors"
              onClick={() => {
                const input = document.querySelector<HTMLInputElement>(`#comment-${id}`);
                if (input && input.value.trim()) {
                  onComment(id, input.value);
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
}
