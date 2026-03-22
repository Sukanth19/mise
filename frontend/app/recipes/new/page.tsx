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
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          type="button"
          onClick={handleBack}
          className="mb-6 flex items-center text-gray-600 hover:text-gray-900 hover:scale-105 transition-all duration-200"
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
          Back to Dashboard
        </button>

        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create New Recipe</h1>
          <p className="mt-2 text-gray-600">
            Add a new recipe to your collection
          </p>
        </div>

        {/* Recipe Form */}
        <RecipeForm onSubmit={handleSubmit} submitLabel="Create Recipe" />
      </div>
    </main>
  );
}
