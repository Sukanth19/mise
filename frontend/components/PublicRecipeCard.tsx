'use client';

import Link from 'next/link';
import LikeButton from './LikeButton';

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

interface PublicRecipeCardProps {
  recipe: PublicRecipe;
}

export default function PublicRecipeCard({ recipe }: PublicRecipeCardProps) {
  const formattedDate = new Date(recipe.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <Link href={`/recipes/${recipe.id}/public`}>
        {recipe.image_url ? (
          <img
            src={recipe.image_url}
            alt={recipe.title}
            className="w-full h-48 object-cover"
          />
        ) : (
          <div className="w-full h-48 bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
            <span className="text-6xl">🍽️</span>
          </div>
        )}
      </Link>

      <div className="p-4">
        <Link href={`/recipes/${recipe.id}/public`}>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            {recipe.title}
          </h3>
        </Link>

        {/* Author Info */}
        <Link
          href={`/users/${recipe.author.id}`}
          className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 mt-2 inline-block"
        >
          by {recipe.author.username}
        </Link>

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {recipe.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
            {recipe.tags.length > 3 && (
              <span className="px-2 py-1 text-gray-600 dark:text-gray-400 text-xs">
                +{recipe.tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Stats and Actions */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
            <LikeButton
              recipeId={recipe.id}
              initialLikesCount={recipe.likes_count}
              initialLiked={false}
            />
            <span className="flex items-center gap-1">
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
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              {recipe.comments_count}
            </span>
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-500">
            {formattedDate}
          </span>
        </div>
      </div>
    </div>
  );
}
