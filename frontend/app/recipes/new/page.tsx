'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { RecipeCreate, Recipe, RecipeUpdate } from '@/types';
import RecipeForm from '@/components/RecipeForm';

export default function NewRecipePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }
    setMounted(true);
  }, [router]);

  const handleSubmit = async (data: RecipeCreate | RecipeUpdate) => {
    const createdRecipe = await apiClient<Recipe>('/api/recipes', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // Redirect to the newly created recipe's detail page
    router.push(`/recipes/${createdRecipe.id}`);
  };

  const handleBack = () => {
    router.push('/dashboard');
  };

  if (!mounted) {
    return (
      <main className="min-h-screen bg-background p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading...</p>
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
          className="mb-8 comic-button bg-card text-foreground px-6 py-3 flex items-center gap-2"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={3}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          <span className="font-bold">BACK</span>
        </button>

        {/* Page Header */}
        <div className="mb-10 comic-panel p-8">
          <h1 className="text-5xl comic-heading text-foreground mb-3">Create New Recipe</h1>
          <p className="text-lg text-muted-foreground font-medium">
            Add a new recipe to your collection
          </p>
        </div>

        {/* Recipe Form */}
        <RecipeForm onSubmit={handleSubmit} submitLabel="Create Recipe" />
      </div>
    </main>
  );
}
