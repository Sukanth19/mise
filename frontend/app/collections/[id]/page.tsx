'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { Collection, Recipe } from '@/types';
import RecipeGrid from '@/components/RecipeGrid';
import CollectionTree from '@/components/CollectionTree';
import AddToCollectionModal from '@/components/AddToCollectionModal';
import { motion } from 'framer-motion';
import { ArrowLeft, Plus, Share2, Folder, X } from 'lucide-react';

interface CollectionWithRecipes extends Collection {
  recipes: Recipe[];
  sub_collections?: Collection[];
}

export default function CollectionDetailPage() {
  const router = useRouter();
  const params = useParams();
  const collectionId = params.id as string;

  const [collection, setCollection] = useState<CollectionWithRecipes | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddRecipesModal, setShowAddRecipesModal] = useState(false);
  const [allRecipes, setAllRecipes] = useState<Recipe[]>([]);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [showShareModal, setShowShareModal] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchCollection();
    fetchAllRecipes();
  }, [collectionId, router]);

  const fetchCollection = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient<CollectionWithRecipes>(`/api/collections/${collectionId}`);
      setCollection(data);
    } catch (err) {
      if (err instanceof Error && err.message.includes('404')) {
        setError('Collection not found');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to fetch collection');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchAllRecipes = async () => {
    try {
      const data = await apiClient<Recipe[]>('/api/recipes');
      setAllRecipes(data);
    } catch (err) {
      console.error('Failed to fetch recipes:', err);
    }
  };

  const handleAddRecipes = async (recipeIds: number[]) => {
    try {
      await apiClient(`/api/collections/${collectionId}/recipes`, {
        method: 'POST',
        body: JSON.stringify({ recipe_ids: recipeIds }),
      });
      setShowAddRecipesModal(false);
      await fetchCollection();
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to add recipes');
    }
  };

  const handleGenerateShareLink = async () => {
    try {
      const data = await apiClient<{ share_url: string; share_token: string }>(
        `/api/collections/${collectionId}/share`,
        { method: 'POST' }
      );
      setShareUrl(data.share_url);
      setShowShareModal(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to generate share link');
    }
  };

  const handleRevokeShare = async () => {
    try {
      await apiClient(`/api/collections/${collectionId}/share`, {
        method: 'DELETE',
      });
      setShareUrl(null);
      setShowShareModal(false);
      await fetchCollection();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to revoke sharing');
    }
  };

  const handleCopyShareLink = () => {
    if (shareUrl) {
      navigator.clipboard.writeText(shareUrl);
      alert('Share link copied to clipboard!');
    }
  };

  const handleBack = () => {
    router.push('/collections');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <p className="text-muted-foreground font-black text-2xl uppercase">Loading collection...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !collection) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <h2 className="text-2xl font-black text-foreground mb-4 uppercase">
              {error === 'Collection not found' ? 'Collection Not Found' : 'Error'}
            </h2>
            <p className="text-muted-foreground mb-6 font-bold">
              {error || 'Unable to load collection'}
            </p>
            <button
              type="button"
              onClick={handleBack}
              className="comic-button px-6 py-3 bg-primary text-primary-foreground"
            >
              BACK TO COLLECTIONS
            </button>
          </div>
        </div>
      </main>
    );
  }

  // Construct full image URL
  const imageUrl = collection.cover_image_url 
    ? `http://localhost:8000${collection.cover_image_url}` 
    : null;

  // Get recipes that are not already in this collection for the add modal
  const availableRecipes = allRecipes.filter(
    recipe => !collection.recipes.some(r => r.id === recipe.id)
  );

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-7xl mx-auto">
        {/* Back Button */}
        <button
          type="button"
          onClick={handleBack}
          className="mb-6 flex items-center text-muted-foreground hover:text-foreground transition-all duration-200 font-bold"
        >
          <ArrowLeft size={20} className="mr-2" strokeWidth={3} />
          BACK TO COLLECTIONS
        </button>

        {/* Collection Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="comic-panel mb-8 overflow-hidden"
        >
          {imageUrl && (
            <div className="w-full h-64 bg-muted overflow-hidden">
              <img
                src={imageUrl}
                alt={collection.name}
                className="w-full h-full object-cover"
              />
            </div>
          )}
          <div className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="text-4xl comic-heading text-foreground mb-2">
                  {collection.name}
                </h1>
                {collection.description && (
                  <p className="text-muted-foreground font-medium text-lg">
                    {collection.description}
                  </p>
                )}
              </div>
              <button
                type="button"
                onClick={handleGenerateShareLink}
                className="comic-button px-4 py-2 bg-secondary text-secondary-foreground flex items-center gap-2"
                aria-label="Share collection"
              >
                <Share2 size={18} strokeWidth={2.5} />
                SHARE
              </button>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground font-bold">
              <span>{collection.recipes.length} RECIPES</span>
              {collection.nesting_level > 0 && (
                <span>LEVEL {collection.nesting_level}</span>
              )}
            </div>
          </div>
        </motion.div>

        {/* Sub-collections */}
        {collection.sub_collections && collection.sub_collections.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="mb-8"
          >
            <h2 className="text-2xl comic-heading text-foreground mb-4">SUB-COLLECTIONS</h2>
            <CollectionTree collections={collection.sub_collections} />
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="mb-8"
        >
          <button
            type="button"
            onClick={() => setShowAddRecipesModal(true)}
            className="comic-button px-6 py-3 bg-primary text-primary-foreground flex items-center gap-2"
          >
            <Plus size={20} strokeWidth={3} />
            ADD RECIPES
          </button>
        </motion.div>

        {/* Recipes */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <h2 className="text-2xl comic-heading text-foreground mb-4">RECIPES</h2>
          {collection.recipes.length === 0 ? (
            <div className="text-center py-12 comic-panel">
              <div className="text-6xl mb-4">🍳</div>
              <p className="text-muted-foreground font-bold text-lg">No recipes in this collection</p>
              <p className="text-muted-foreground text-sm mt-2">Add recipes to get started</p>
            </div>
          ) : (
            <RecipeGrid recipes={collection.recipes} />
          )}
        </motion.div>

        {/* Add Recipes Modal */}
        <AddToCollectionModal
          isOpen={showAddRecipesModal}
          onClose={() => setShowAddRecipesModal(false)}
          onSubmit={async (recipeIds) => {
            await handleAddRecipes(recipeIds);
          }}
          collections={[collection]}
          initialSelectedIds={[collection.id]}
        />

        {/* Share Modal */}
        {showShareModal && (
          <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                setShowShareModal(false);
              }
            }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="share-modal-title"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="comic-panel bg-card w-full max-w-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b-4 border-border">
                <h2 id="share-modal-title" className="text-2xl font-black uppercase tracking-wide">
                  Share Collection
                </h2>
                <button
                  type="button"
                  onClick={() => setShowShareModal(false)}
                  className="comic-button p-2 bg-secondary text-secondary-foreground"
                  aria-label="Close modal"
                >
                  <X size={20} />
                </button>
              </div>
              <div className="p-6">
                <p className="text-muted-foreground font-medium mb-4">
                  Anyone with this link can view this collection:
                </p>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    value={shareUrl || ''}
                    readOnly
                    className="flex-1 comic-input px-4 py-2 font-mono text-sm"
                  />
                  <button
                    type="button"
                    onClick={handleCopyShareLink}
                    className="comic-button px-4 py-2 bg-primary text-primary-foreground"
                  >
                    COPY
                  </button>
                </div>
                <button
                  type="button"
                  onClick={handleRevokeShare}
                  className="comic-button px-4 py-2 bg-destructive text-destructive-foreground"
                >
                  REVOKE SHARING
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </main>
  );
}
