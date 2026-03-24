'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { ShoppingList } from '@/types';
import ShoppingListCard from '@/components/ShoppingListCard';
import EmptyState from '@/components/EmptyState';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingCart, Plus, X } from 'lucide-react';

export default function ShoppingListsPage() {
  const router = useRouter();
  const [shoppingLists, setShoppingLists] = useState<ShoppingList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [selectedList, setSelectedList] = useState<ShoppingList | null>(null);
  const [shareUrl, setShareUrl] = useState<string>('');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchShoppingLists();
  }, [router]);

  const fetchShoppingLists = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient<{ shopping_lists: ShoppingList[] }>('/api/shopping-lists');
      setShoppingLists(data.shopping_lists);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch shopping lists');
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async (shoppingList: ShoppingList) => {
    try {
      const data = await apiClient<{ share_url: string; share_token: string }>(
        `/api/shopping-lists/${shoppingList.id}/share`,
        { method: 'POST' }
      );
      setShareUrl(data.share_url);
      setSelectedList(shoppingList);
      setShowShareModal(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to generate share link');
    }
  };

  const handleDelete = async (shoppingList: ShoppingList) => {
    if (!confirm(`Delete "${shoppingList.name}"?`)) return;

    try {
      await apiClient(`/api/shopping-lists/${shoppingList.id}`, {
        method: 'DELETE',
      });
      await fetchShoppingLists();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete shopping list');
    }
  };

  const copyShareUrl = () => {
    navigator.clipboard.writeText(shareUrl);
    alert('Share link copied to clipboard!');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <p className="text-muted-foreground font-black text-2xl uppercase">Loading shopping lists...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <h1 className="text-4xl comic-heading text-foreground mb-4 md:mb-0">SHOPPING LISTS</h1>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="comic-button px-8 py-4 bg-primary text-primary-foreground rounded-none flex items-center gap-2"
            data-testid="create-button"
          >
            <Plus size={20} strokeWidth={3} />
            CREATE SHOPPING LIST
          </button>
        </div>

        {error && (
          <div className="mb-6 comic-panel bg-destructive text-destructive-foreground p-4 rounded-none font-bold">
            {error}
          </div>
        )}

        {!loading && shoppingLists.length === 0 && (
          <EmptyState
            icon={<ShoppingCart size={64} strokeWidth={3} />}
            message="No shopping lists yet"
            description="Create a shopping list from your recipes or meal plan to get started!"
            action={{
              label: 'CREATE SHOPPING LIST',
              onClick: () => setShowCreateModal(true),
            }}
          />
        )}

        {!loading && shoppingLists.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {shoppingLists.map((list, index) => (
              <ShoppingListCard
                key={list.id}
                shoppingList={list}
                index={index}
                onShare={handleShare}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}

        {/* Create Shopping List Modal */}
        <AnimatePresence>
          {showCreateModal && (
            <div
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
              onClick={(e) => {
                if (e.target === e.currentTarget) {
                  setShowCreateModal(false);
                }
              }}
              role="dialog"
              aria-modal="true"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                transition={{ duration: 0.2 }}
                className="comic-panel bg-card w-full max-w-md"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between p-6 border-b-4 border-border">
                  <h2 className="text-2xl font-black uppercase tracking-wide">
                    Create Shopping List
                  </h2>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="comic-button p-2 bg-secondary text-secondary-foreground"
                    aria-label="Close modal"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="p-6 space-y-4">
                  <p className="text-muted-foreground font-medium">
                    Choose how to create your shopping list:
                  </p>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      router.push('/recipes');
                    }}
                    className="comic-button w-full p-4 bg-primary text-primary-foreground hover:bg-primary/80 text-left"
                  >
                    <div className="font-bold">FROM RECIPES</div>
                    <div className="text-sm opacity-90">Select recipes to add to your list</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      router.push('/meal-planner');
                    }}
                    className="comic-button w-full p-4 bg-primary text-primary-foreground hover:bg-primary/80 text-left"
                  >
                    <div className="font-bold">FROM MEAL PLAN</div>
                    <div className="text-sm opacity-90">Generate from your meal plan dates</div>
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Share Modal */}
        <AnimatePresence>
          {showShareModal && selectedList && (
            <div
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
              onClick={(e) => {
                if (e.target === e.currentTarget) {
                  setShowShareModal(false);
                  setSelectedList(null);
                }
              }}
              role="dialog"
              aria-modal="true"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                transition={{ duration: 0.2 }}
                className="comic-panel bg-card w-full max-w-md"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between p-6 border-b-4 border-border">
                  <h2 className="text-2xl font-black uppercase tracking-wide">
                    Share Shopping List
                  </h2>
                  <button
                    type="button"
                    onClick={() => {
                      setShowShareModal(false);
                      setSelectedList(null);
                    }}
                    className="comic-button p-2 bg-secondary text-secondary-foreground"
                    aria-label="Close modal"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="p-6 space-y-4">
                  <p className="text-muted-foreground font-medium">
                    Share this link with others:
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={shareUrl}
                      readOnly
                      className="flex-1 p-3 border-4 border-border bg-background text-foreground font-medium"
                      aria-label="Share URL"
                    />
                    <button
                      type="button"
                      onClick={copyShareUrl}
                      className="comic-button px-4 bg-primary text-primary-foreground hover:bg-primary/80"
                    >
                      COPY
                    </button>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
