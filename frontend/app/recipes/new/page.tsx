'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { RecipeCreate, Recipe, RecipeUpdate } from '@/types';
import RecipeForm from '@/components/RecipeForm';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function NewRecipePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importUrl, setImportUrl] = useState('');
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importedData, setImportedData] = useState<RecipeUpdate | null>(null);

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }
    setMounted(true);
  }, [router]);

  const handleImportFromUrl = async () => {
    if (!importUrl.trim()) {
      setImportError('Please enter a URL');
      return;
    }

    try {
      setImporting(true);
      setImportError(null);

      const recipe = await apiClient<Recipe>('/api/recipes/import-url', {
        method: 'POST',
        body: JSON.stringify({ url: importUrl }),
        requiresAuth: true,
      });

      // Set the imported data to pre-fill the form
      setImportedData({
        title: recipe.title,
        image_url: recipe.image_url,
        ingredients: recipe.ingredients,
        steps: recipe.steps,
        tags: recipe.tags,
        reference_link: recipe.reference_link,
      });

      setShowImportModal(false);
      setImportUrl('');
    } catch (err) {
      setImportError(err instanceof Error ? err.message : 'Failed to import recipe');
    } finally {
      setImporting(false);
    }
  };

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
      <main className="min-h-screen bg-background p-8 flex items-center justify-center">
        <LoadingSpinner variant="recipe" size="lg" />
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-5xl comic-heading text-foreground mb-3">Create New Recipe</h1>
              <p className="text-lg text-muted-foreground font-medium">
                Add a new recipe to your collection
              </p>
            </div>
            <button
              type="button"
              onClick={() => setShowImportModal(true)}
              className="comic-button bg-secondary text-secondary-foreground px-6 py-3 flex items-center gap-2"
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
                  strokeWidth={3}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                />
              </svg>
              <span className="font-bold">IMPORT FROM URL</span>
            </button>
          </div>
        </div>

        {/* Recipe Form */}
        <RecipeForm 
          onSubmit={handleSubmit} 
          submitLabel="Create Recipe"
          initialData={importedData || undefined}
        />

        {/* Import Modal */}
        {showImportModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-background comic-border max-w-md w-full p-6">
              <h2 className="text-2xl comic-heading text-foreground mb-4">
                IMPORT FROM URL
              </h2>
              <p className="text-muted-foreground mb-4 font-medium">
                Enter the URL of a recipe to import its content
              </p>

              <input
                type="url"
                value={importUrl}
                onChange={(e) => setImportUrl(e.target.value)}
                placeholder="https://example.com/recipe"
                className="w-full comic-input px-4 py-3 mb-4 font-medium"
                disabled={importing}
              />

              {importError && (
                <div className="comic-border bg-destructive/10 border-destructive text-destructive px-4 py-3 mb-4 font-bold">
                  ⚠️ {importError}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleImportFromUrl}
                  disabled={importing}
                  className="flex-1 comic-button bg-primary text-primary-foreground py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {importing ? 'IMPORTING...' : 'IMPORT'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowImportModal(false);
                    setImportUrl('');
                    setImportError(null);
                  }}
                  disabled={importing}
                  className="flex-1 comic-button bg-card text-foreground py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  CANCEL
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
