'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { Recipe } from '@/types';
import RecipeGrid from '@/components/RecipeGrid';
import SearchBar from '@/components/SearchBar';

export default function DashboardPage() {
  const router = useRouter();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchRecipes();
  }, [router]);

  const fetchRecipes = async (search?: string) => {
    try {
      setLoading(true);
      setError(null);
      const endpoint = search ? `/api/recipes?search=${encodeURIComponent(search)}` : '/api/recipes';
      const data = await apiClient<Recipe[]>(endpoint);
      setRecipes(data);
      setFilteredRecipes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recipes');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    fetchRecipes(query.trim() === '' ? undefined : query);
  };

  const handleCreateRecipe = () => {
    router.push('/recipes/new');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <p className="text-muted-foreground font-black text-2xl uppercase">Loading recipes...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <h1 className="text-4xl comic-heading text-foreground mb-4 md:mb-0">MY RECIPES</h1>
          <button
            type="button"
            onClick={handleCreateRecipe}
            className="comic-button px-8 py-4 bg-primary text-primary-foreground rounded-none"
          >
            CREATE RECIPE
          </button>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} value={searchQuery} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 comic-panel bg-destructive text-destructive-foreground p-4 rounded-none font-bold">
            {error}
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredRecipes && filteredRecipes.length === 0 && !searchQuery && (
          <div className="text-center py-12">
            <div className="mb-6">
              <svg
                className="mx-auto h-32 w-32 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={3}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-black text-foreground mb-3 uppercase">No recipes yet</h2>
            <p className="text-muted-foreground mb-8 font-bold uppercase">Start building your recipe collection!</p>
            <button
              type="button"
              onClick={handleCreateRecipe}
              className="comic-button px-8 py-4 bg-primary text-primary-foreground rounded-none"
            >
              CREATE YOUR FIRST RECIPE
            </button>
          </div>
        )}

        {/* Search Results Empty State */}
        {!loading && filteredRecipes && filteredRecipes.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <p className="text-muted-foreground font-bold uppercase">No recipes found matching "{searchQuery}"</p>
          </div>
        )}

        {/* Recipe Grid */}
        {!loading && filteredRecipes && filteredRecipes.length > 0 && (
          <RecipeGrid recipes={filteredRecipes} />
        )}
      </div>
    </main>
  );
}
