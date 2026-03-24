'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { ShoppingList, CustomItemCreate } from '@/types';
import ShoppingListDetail from '@/components/ShoppingListDetail';
import AddCustomItemForm from '@/components/AddCustomItemForm';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, X } from 'lucide-react';

export default function ShoppingListDetailPage() {
  const router = useRouter();
  const params = useParams();
  const listId = params.id as string;

  const [shoppingList, setShoppingList] = useState<ShoppingList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareUrl, setShareUrl] = useState<string>('');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchShoppingList();
  }, [router, listId]);

  const fetchShoppingList = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient<ShoppingList>(`/api/shopping-lists/${listId}`);
      setShoppingList(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch shopping list');
    } finally {
      setLoading(false);
    }
  };

  const handleItemCheck = async (itemId: number, isChecked: boolean) => {
    if (!shoppingList) return;

    try {
      await apiClient(`/api/shopping-lists/${listId}/items/${itemId}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_checked: isChecked }),
      });
      
      // Update local state
      setShoppingList({
        ...shoppingList,
        items: shoppingList.items?.map(item =>
          item.id === itemId ? { ...item, is_checked: isChecked } : item
        ),
      });
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update item');
    }
  };

  const handleItemDelete = async (itemId: number) => {
    if (!shoppingList) return;

    try {
      await apiClient(`/api/shopping-lists/${listId}/items/${itemId}`, {
        method: 'DELETE',
      });
      
      // Update local state
      setShoppingList({
        ...shoppingList,
        items: shoppingList.items?.filter(item => item.id !== itemId),
      });
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete item');
    }
  };

  const handleAddCustomItem = async (item: CustomItemCreate) => {
    if (!shoppingList) return;

    try {
      const newItem = await apiClient(`/api/shopping-lists/${listId}/items`, {
        method: 'POST',
        body: JSON.stringify(item),
      });
      
      // Refresh the shopping list to get updated items
      await fetchShoppingList();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add item');
    }
  };

  const handleShare = async () => {
    if (!shoppingList) return;

    try {
      const data = await apiClient<{ share_url: string; share_token: string }>(
        `/api/shopping-lists/${listId}/share`,
        { method: 'POST' }
      );
      setShareUrl(data.share_url);
      setShowShareModal(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to generate share link');
    }
  };

  const copyShareUrl = () => {
    navigator.clipboard.writeText(shareUrl);
    alert('Share link copied to clipboard!');
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <p className="text-muted-foreground font-black text-2xl uppercase">Loading shopping list...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !shoppingList) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8">
        <div className="max-w-4xl mx-auto">
          <div className="comic-panel bg-destructive text-destructive-foreground p-6 rounded-none font-bold">
            {error || 'Shopping list not found'}
          </div>
          <button
            type="button"
            onClick={() => router.push('/shopping-lists')}
            className="comic-button mt-4 px-6 py-3 bg-primary text-primary-foreground"
          >
            <ArrowLeft size={20} className="inline mr-2" />
            BACK TO SHOPPING LISTS
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-4xl mx-auto">
        <button
          type="button"
          onClick={() => router.push('/shopping-lists')}
          className="comic-button mb-6 px-6 py-3 bg-secondary text-secondary-foreground flex items-center gap-2"
        >
          <ArrowLeft size={20} />
          BACK TO LISTS
        </button>

        <ShoppingListDetail
          shoppingList={shoppingList}
          onItemCheck={handleItemCheck}
          onItemDelete={handleItemDelete}
          onShare={handleShare}
        />

        <div className="mt-6">
          <AddCustomItemForm onAdd={handleAddCustomItem} />
        </div>

        {shoppingList.share_token && (
          <div className="mt-6 comic-panel p-4 bg-card">
            <p className="text-sm font-bold text-muted-foreground">
              This shopping list is shared. Others can view and check off items.
            </p>
          </div>
        )}

        {/* Share Modal */}
        <AnimatePresence>
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
                    onClick={() => setShowShareModal(false)}
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
