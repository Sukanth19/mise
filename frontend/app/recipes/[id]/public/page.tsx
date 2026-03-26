'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import Link from 'next/link';
import LikeButton from '@/components/LikeButton';
import CommentList from '@/components/CommentList';
import CommentForm from '@/components/CommentForm';
import ShareButtons from '@/components/ShareButtons';
import QRCodeDisplay from '@/components/QRCodeDisplay';
import LoadingSkeleton from '@/components/LoadingSkeleton';

interface Comment {
  id: number;
  recipe_id: number;
  user_id: number;
  comment_text: string;
  created_at: string;
  author: {
    id: number;
    username: string;
  };
}

interface PublicRecipe {
  id: number;
  title: string;
  image_url?: string;
  ingredients: string[];
  steps: string[];
  tags?: string[];
  reference_link?: string;
  created_at: string;
  author: {
    id: number;
    username: string;
  };
  likes_count: number;
  comments: Comment[];
}

export default function PublicRecipePage() {
  const params = useParams();
  const router = useRouter();
  const recipeId = parseInt(params.id as string);
  
  const [recipe, setRecipe] = useState<PublicRecipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forking, setForking] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);

  useEffect(() => {
    fetchRecipe();
  }, [recipeId]);

  const fetchRecipe = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await apiClient<PublicRecipe>(
        `/api/recipes/public/${recipeId}`,
        { requiresAuth: false }
      );

      setRecipe(data);
      setComments(data.comments || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recipe');
    } finally {
      setLoading(false);
    }
  };

  const handleFork = async () => {
    const token = getToken();
    if (!token) {
      alert('Please log in to fork recipes');
      router.push('/');
      return;
    }

    try {
      setForking(true);
      const forkedRecipe = await apiClient<{ id: number }>(
        `/api/recipes/${recipeId}/fork`,
        {
          method: 'POST',
          requiresAuth: true,
        }
      );

      alert('Recipe forked successfully!');
      router.push(`/recipes/${forkedRecipe.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to fork recipe');
    } finally {
      setForking(false);
    }
  };

  const handleCommentAdded = (comment: Comment) => {
    setComments([...comments, comment]);
    if (recipe) {
      setRecipe({
        ...recipe,
        comments: [...comments, comment],
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <LoadingSkeleton variant="recipe-card" count={1} />
        </div>
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-red-600 dark:text-red-400 mb-4">
              {error || 'Recipe not found'}
            </p>
            <Link
              href="/discover"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              Back to Discovery
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Recipe Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-6">
          {/* Recipe Image */}
          {recipe.image_url ? (
            <img
              src={recipe.image_url}
              alt={recipe.title}
              className="w-full h-96 object-cover"
            />
          ) : (
            <div className="w-full h-96 bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
              <span className="text-9xl">🍽️</span>
            </div>
          )}

          {/* Recipe Info */}
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              {recipe.title}
            </h1>

            {/* Author Info */}
            <div className="flex items-center gap-4 mb-4">
              <Link
                href={`/users/${recipe.author.id}`}
                className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
              >
                <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {recipe.author.username.charAt(0).toUpperCase()}
                </div>
                <span className="font-medium">{recipe.author.username}</span>
              </Link>
              <span className="text-gray-400 dark:text-gray-600">•</span>
              <span className="text-sm text-gray-500 dark:text-gray-500">
                {new Date(recipe.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>

            {/* Tags */}
            {recipe.tags && recipe.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-6">
                {recipe.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <LikeButton
                recipeId={recipe.id}
                initialLikesCount={recipe.likes_count}
                initialLiked={false}
              />
              <button
                type="button"
                onClick={handleFork}
                disabled={forking}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
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
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                {forking ? 'Forking...' : 'Fork Recipe'}
              </button>
            </div>
          </div>
        </div>

        {/* Recipe Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Ingredients */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                Ingredients
              </h2>
              <ul className="space-y-2">
                {recipe.ingredients.map((ingredient, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-gray-700 dark:text-gray-300"
                  >
                    <span className="text-blue-600 dark:text-blue-400 mt-1">•</span>
                    <span>{ingredient}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Steps */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                Instructions
              </h2>
              <ol className="space-y-4">
                {recipe.steps.map((step, index) => (
                  <li key={index} className="flex gap-4">
                    <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                      {index + 1}
                    </span>
                    <p className="text-gray-700 dark:text-gray-300 pt-1">{step}</p>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </div>

        {/* Reference Link */}
        {recipe.reference_link && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">
              Original Source
            </h3>
            <a
              href={recipe.reference_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 hover:underline break-all"
            >
              {recipe.reference_link}
            </a>
          </div>
        )}

        {/* Share Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ShareButtons recipeId={recipe.id} />
            <QRCodeDisplay recipeId={recipe.id} />
          </div>
        </div>

        {/* Comments Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            Comments ({comments.length})
          </h2>

          {/* Comment Form */}
          <div className="mb-6">
            <CommentForm
              recipeId={recipe.id}
              onCommentAdded={handleCommentAdded}
            />
          </div>

          {/* Comment List */}
          <CommentList comments={comments} />
        </div>
      </div>
    </div>
  );
}
