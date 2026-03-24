'use client';

import { useState } from 'react';
import { apiClient, getToken } from '@/lib/api';

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

interface CommentFormProps {
  recipeId: number;
  onCommentAdded: (comment: Comment) => void;
}

export default function CommentForm({ recipeId, onCommentAdded }: CommentFormProps) {
  const [commentText, setCommentText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Check if user is authenticated
    const token = getToken();
    if (!token) {
      setError('Please log in to comment');
      return;
    }

    if (!commentText.trim()) {
      setError('Comment cannot be empty');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const comment = await apiClient<Comment>(
        `/api/recipes/${recipeId}/comments`,
        {
          method: 'POST',
          body: JSON.stringify({ comment_text: commentText }),
          requiresAuth: true,
        }
      );

      onCommentAdded(comment);
      setCommentText('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add comment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <textarea
          value={commentText}
          onChange={(e) => setCommentText(e.target.value)}
          placeholder="Add a comment..."
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          disabled={loading}
        />
      </div>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading || !commentText.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
              Posting...
            </span>
          ) : (
            'Post Comment'
          )}
        </button>
      </div>
    </form>
  );
}
