'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ShoppingList } from '@/types';
import ShoppingListDetail from '@/components/ShoppingListDetail';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SharedShoppingListPage() {
  const params = useParams();
  const token = params.token as string;

  const [shoppingList, setShoppingList] = useState<ShoppingList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSharedShoppingList();
  }, [token]);

  const fetchSharedShoppingList = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/api/shopping-lists/shared/${token}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch shared shopping list');
      }
      
      const data = await response.json();
      setShoppingList(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch shared shopping list');
    } finally {
      setLoading(false);
    }
  };

  const handleItemCheck = async (itemId: number, isChecked: boolean) => {
    if (!shoppingList) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/shopping-lists/shared/${token}/items/${itemId}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ is_checked: isChecked }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update item');
      }

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
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 comic-panel p-4 bg-card">
          <p className="text-sm font-bold text-muted-foreground">
            You are viewing a shared shopping list. You can check off items as you shop.
          </p>
        </div>

        <ShoppingListDetail
          shoppingList={shoppingList}
          onItemCheck={handleItemCheck}
        />
      </div>
    </main>
  );
}
