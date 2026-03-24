'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import PublicRecipeCard from './PublicRecipeCard';
import LoadingSkeleton from './LoadingSkeleton';
import EmptyState from './EmptyState';

interface PublicRecipe {
  id: number;
  title: string;
  image_url?: string;
  ingredients: string[];
  steps: string[];
  tags?: string[];
  created_at: string;
  author: {
    id: number;
    username: string;
  };
  likes_count: number;
  comments_count: number;
}

interface DiscoveryFeedResponse {
  recipes: PublicRecipe[];
  total: number;
  page: number;
}

interface DiscoveryFeedProps {
  searchQuery?: string;
}

export default function DiscoveryFeed({ searchQuery = '' }: DiscoveryFeedProps) {
  const [recipes, setRecipes] = useState<PublicRecipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState(searchQuery);
  const limit = 20;

  useEffect(() => {
    fetchRecipes();
  }, [page, search]);

  const fetchRecipes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const queryParams = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });
      
      if (search) {
        queryParams.append('search', search);
      }

      const data = await apiClient<DiscoveryFeedResponse>(
        `/api/recipes/discover?${queryParams.toString()}`,
        { requiresAuth: false }
      );

      setRecipes(data.recipes);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recipes');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setPage(1);
    fetchRecipes();
  };

  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const handleNextPage = () => {
    if (page * limit < total) {
      setPage(page + 1);
    }
  };

  const totalPages = Math.ceil(total / limit);

  if (loading && recipes.length === 0) {
    return (
      <div className="space-y-4">
        <LoadingSkeleton variant="recipe-card" count={6} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 dark:text-red-400">{error}</p>
        <button
          onClick={fetchRecipes}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search public recipes..."
          className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </form>

      {/* Recipe Grid */}
      {recipes.length === 0 ? (
        <EmptyState
          icon="🔍"
          message={search ? 'No recipes found matching your search' : 'No public recipes yet'}
          actionText={search ? 'Clear search' : undefined}
          onAction={search ? () => { setSearch(''); setPage(1); } : undefined}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recipes.map((recipe) => (
              <PublicRecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={handlePrevPage}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              
              <span className="text-gray-700 dark:text-gray-300">
                Page {page} of {totalPages}
              </span>
              
              <button
                onClick={handleNextPage}
                disabled={page >= totalPages}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
