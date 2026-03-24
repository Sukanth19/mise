'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import FollowButton from './FollowButton';
import PublicRecipeCard from './PublicRecipeCard';
import LoadingSkeleton from './LoadingSkeleton';
import EmptyState from './EmptyState';

interface User {
  id: number;
  username: string;
}

interface PublicRecipe {
  id: number;
  title: string;
  image_url?: string;
  tags?: string[];
  created_at: string;
  author: {
    id: number;
    username: string;
  };
  likes_count: number;
  comments_count: number;
}

interface UserProfileData {
  user: User;
  followers_count: number;
  following_count: number;
  public_recipes: PublicRecipe[];
}

interface UserProfileProps {
  userId: number;
  currentUserId?: number;
}

export default function UserProfile({ userId, currentUserId }: UserProfileProps) {
  const [profileData, setProfileData] = useState<UserProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProfile();
  }, [userId]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch user info and followers/following counts
      const [followersData, followingData] = await Promise.all([
        apiClient<{ followers: User[]; count: number }>(
          `/api/users/${userId}/followers`,
          { requiresAuth: false }
        ),
        apiClient<{ following: User[]; count: number }>(
          `/api/users/${userId}/following`,
          { requiresAuth: false }
        ),
      ]);

      // Fetch user's public recipes from discovery feed
      const recipesData = await apiClient<{ recipes: PublicRecipe[]; total: number }>(
        `/api/recipes/discover?author_id=${userId}`,
        { requiresAuth: false }
      );

      // Extract user info from first recipe or create basic user object
      const user: User = recipesData.recipes.length > 0
        ? recipesData.recipes[0].author
        : { id: userId, username: `User ${userId}` };

      setProfileData({
        user,
        followers_count: followersData.count,
        following_count: followingData.count,
        public_recipes: recipesData.recipes,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <LoadingSkeleton variant="recipe-card" count={1} />
        </div>
        <LoadingSkeleton variant="recipe-card" count={3} />
      </div>
    );
  }

  if (error || !profileData) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 dark:text-red-400">{error || 'Profile not found'}</p>
        <button
          onClick={fetchProfile}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  const isOwnProfile = currentUserId === userId;

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            {/* Avatar Placeholder */}
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {profileData.user.username.charAt(0).toUpperCase()}
            </div>

            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {profileData.user.username}
              </h1>
              <div className="flex gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                <span>
                  <strong className="text-gray-900 dark:text-gray-100">
                    {profileData.public_recipes.length}
                  </strong>{' '}
                  recipes
                </span>
                <span>
                  <strong className="text-gray-900 dark:text-gray-100">
                    {profileData.followers_count}
                  </strong>{' '}
                  followers
                </span>
                <span>
                  <strong className="text-gray-900 dark:text-gray-100">
                    {profileData.following_count}
                  </strong>{' '}
                  following
                </span>
              </div>
            </div>
          </div>

          {/* Follow Button (only show if not own profile) */}
          {!isOwnProfile && currentUserId && (
            <FollowButton
              userId={userId}
              initialFollowersCount={profileData.followers_count}
              initialFollowing={false}
            />
          )}
        </div>
      </div>

      {/* Public Recipes */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Public Recipes
        </h2>
        {profileData.public_recipes.length === 0 ? (
          <EmptyState
            icon="📝"
            message={
              isOwnProfile
                ? 'You haven\'t shared any public recipes yet'
                : `${profileData.user.username} hasn't shared any public recipes yet`
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {profileData.public_recipes.map((recipe) => (
              <PublicRecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
