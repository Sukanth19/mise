'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';

interface FollowButtonProps {
  userId: number;
  initialFollowersCount: number;
  initialFollowing: boolean;
}

export default function FollowButton({
  userId,
  initialFollowersCount,
  initialFollowing,
}: FollowButtonProps) {
  const [following, setFollowing] = useState(initialFollowing);
  const [followersCount, setFollowersCount] = useState(initialFollowersCount);
  const [loading, setLoading] = useState(false);

  const handleToggleFollow = async () => {
    try {
      setLoading(true);

      if (following) {
        // Unfollow
        const data = await apiClient<{ following: boolean; followers_count: number }>(
          `/api/users/${userId}/follow`,
          {
            method: 'DELETE',
            requiresAuth: true,
          }
        );
        setFollowing(data.following);
        setFollowersCount(data.followers_count);
      } else {
        // Follow
        const data = await apiClient<{ following: boolean; followers_count: number }>(
          `/api/users/${userId}/follow`,
          {
            method: 'POST',
            requiresAuth: true,
          }
        );
        setFollowing(data.following);
        setFollowersCount(data.followers_count);
      }
    } catch (error) {
      console.error('Failed to toggle follow:', error);
      // Optionally show error toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleToggleFollow}
      disabled={loading}
      className={`px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
        following
          ? 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          : 'bg-blue-600 text-white hover:bg-blue-700'
      }`}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          {following ? 'Unfollowing...' : 'Following...'}
        </span>
      ) : (
        <span className="flex items-center gap-2">
          {following ? (
            <>
              <svg
                className="w-4 h-4"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              Following
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Follow
            </>
          )}
        </span>
      )}
    </button>
  );
}
