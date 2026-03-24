'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { Recipe, RecipeUpdate, RecipeCreate } from '@/types';
import RecipeForm from '@/components/RecipeForm';

export default function EditRecipePage() {
  const router = useRouter();
  const params = useParams();
  const recipeId = params.id as string;

  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    // Fetch existing recipe data
    const fetchRecipe = async () => {
      try {
        setLoading(true);
        const data = await apiClient<Recipe>(`/api/recipes/${recipeId}`);
        setRecipe(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load recipe');
      } finally {
        setLoading(false);
      }
    };

    fetchRecipe();
  }, [recipeId, router]);

  const handleSubmit = async (data: RecipeCreate | RecipeUpdate) => {
    // Submit to PUT /api/recipes/{id} endpoint
    const updatedRecipe = await apiClient<Recipe>(`/api/recipes/${recipeId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });

    // Redirect to recipe detail page on success
    router.push(`/recipes/${updatedRecipe.id}`);
  };

  const handleVisibilityChange = async (recipeId: number, visibility: string) => {
    await apiClient(`/api/recipes/${recipeId}/visibility`, {
      method: 'PATCH',
      body: JSON.stringify({ visibility }),
      requiresAuth: true,
    });
  };

  const handleBack = () => {
    router.push(`/recipes/${recipeId}`);
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading recipe...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !recipe) {
    return (
      <main className="min-h-screen bg-background p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <p className="text-destructive">{error || 'Recipe not found'}</p>
            <button
              type="button"
              onClick={() => router.push('/dashboard')}
              className="mt-4 text-primary hover:opacity-80 hover:scale-105 transition-all duration-200"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          type="button"
          onClick={handleBack}
          className="mb-6 flex items-center text-muted-foreground hover:text-foreground hover:scale-105 transition-all duration-200"
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Recipe
        </button>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Edit Recipe</h1>
          <p className="mt-2 text-muted-foreground">
            Update your recipe details
          </p>
        </div>

        {/* Recipe Form - Pre-populated with existing data */}
        <RecipeForm 
          initialData={recipe}
          onSubmit={handleSubmit} 
          submitLabel="Update Recipe"
          onVisibilityChange={handleVisibilityChange}
        />
      </div>
    </main>
  );
}
