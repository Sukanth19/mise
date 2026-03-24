'use client';

import { useState } from 'react';
import { apiClient, getToken } from '@/lib/api';

interface LikeButtonProps {
  recipeId: number;
  initialLikesCount: number;
  initialLiked: boolean;
}

export default function LikeButton({
  recipeId,
  initialLikesCount,
  initialLiked,
}: LikeButtonProps) {
  const [liked, setLiked] = useState(initialLiked);
  const [likesCount, setLikesCount] = useState(initialLikesCount);
  const [loading, setLoading] = useState(false);

  const handleToggleLike = async () => {
    // Check if user is authenticated
    const token = getToken();
    if (!token) {
      // Redirect to login or show message
      alert('Please log in to like recipes');
      return;
    }

    try {
      setLoading(true);

      if (liked) {
        // Unlike
        const data = await apiClient<{ liked: boolean; likes_count: number }>(
          `/api/recipes/${recipeId}/like`,
          {
            method: 'DELETE',
            requiresAuth: true,
          }
        );
        setLiked(data.liked);
        setLikesCount(data.likes_count);
      } else {
        // Like
        const data = await apiClient<{ liked: boolean; likes_count: number }>(
          `/api/recipes/${recipeId}/like`,
          {
            method: 'POST',
            requiresAuth: true,
          }
        );
        setLiked(data.liked);
        setLikesCount(data.likes_count);
      }
    } catch (error) {
      console.error('Failed to toggle like:', error);
      // Optionally show error toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleToggleLike}
      disabled={loading}
      className="flex items-center gap-1 text-gray-600 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {liked ? (
        <svg
          className="w-5 h-5 text-red-500 fill-current"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
            clipRule="evenodd"
          />
        </svg>
      ) : (
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
        </svg>
      )}
      <span className={liked ? 'text-red-500' : ''}>{likesCount}</span>
    </button>
  );
}
