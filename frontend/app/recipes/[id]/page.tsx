'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { Recipe } from '@/types';
import RecipeDetail from '@/components/RecipeDetail';
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal';

export default function RecipeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const recipeId = params.id as string;

  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchRecipe();
  }, [recipeId, router]);

  const fetchRecipe = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient<Recipe>(`/api/recipes/${recipeId}`);
      setRecipe(data);
    } catch (err) {
      if (err instanceof Error && err.message.includes('404')) {
        setError('Recipe not found');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to fetch recipe');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    router.push(`/recipes/${recipeId}/edit`);
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await apiClient(`/api/recipes/${recipeId}`, {
        method: 'DELETE',
      });
      setShowDeleteModal(false);
      router.push('/dashboard');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete recipe');
      setDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const handleBack = () => {
    router.push('/dashboard');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <p className="text-gray-600">Loading recipe...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !recipe) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">
              {error === 'Recipe not found' ? 'Recipe Not Found' : 'Error'}
            </h2>
            <p className="text-gray-600 mb-6">
              {error || 'Unable to load recipe'}
            </p>
            <button
              type="button"
              onClick={handleBack}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 hover:shadow-lg hover:scale-105 transition-all duration-200"
            >
              Back to Dashboard
            </button>
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

        {/* Recipe Detail */}
        <RecipeDetail recipe={recipe} />

        {/* Action Buttons */}
        <div className="mt-8 flex gap-4 justify-center">
          <button
            type="button"
            onClick={handleEdit}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 hover:shadow-lg hover:scale-105 transition-all duration-200 font-semibold"
          >
            Edit Recipe
          </button>
          <button
            type="button"
            onClick={() => setShowDeleteModal(true)}
            disabled={deleting}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 hover:shadow-lg hover:scale-105 transition-all duration-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none"
          >
            Delete Recipe
          </button>
        </div>

        {/* Delete Confirmation Modal */}
        <DeleteConfirmationModal
          isOpen={showDeleteModal}
          onClose={() => setShowDeleteModal(false)}
          onConfirm={handleDelete}
          title={recipe.title}
          isDeleting={deleting}
        />
      </div>
    </main>
  );
}
