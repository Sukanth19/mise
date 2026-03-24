'use client';

import { ShoppingList, ShoppingListItem } from '@/types';
import { Share2 } from 'lucide-react';
import CategorySection from './CategorySection';

interface ShoppingListDetailProps {
  shoppingList: ShoppingList;
  onItemCheck?: (itemId: number, isChecked: boolean) => void;
  onItemDelete?: (itemId: number) => void;
  onShare?: () => void;
}

export default function ShoppingListDetail({ 
  shoppingList,
  onItemCheck,
  onItemDelete,
  onShare
}: ShoppingListDetailProps) {
  const items = shoppingList.items || [];
  const checkedCount = items.filter(item => item.is_checked).length;
  const totalCount = items.length;
  const progressPercentage = totalCount > 0 ? (checkedCount / totalCount) * 100 : 0;

  const itemsByCategory = items.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = [];
    }
    acc[item.category].push(item);
    return acc;
  }, {} as Record<string, ShoppingListItem[]>);

  const categories: Array<'produce' | 'dairy' | 'meat' | 'pantry' | 'other'> = [
    'produce',
    'dairy',
    'meat',
    'pantry',
    'other'
  ];

  return (
    <div className="space-y-6">
      <div className="comic-panel p-6 bg-card">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-black text-foreground uppercase tracking-wide">
            {shoppingList.name}
          </h1>
          {onShare && (
            <button
              type="button"
              onClick={onShare}
              className="comic-button p-3 bg-primary text-primary-foreground hover:bg-primary/80 flex items-center gap-2"
              aria-label="Share shopping list"
              data-testid="share-button"
            >
              <Share2 size={20} />
              <span className="font-bold">SHARE</span>
            </button>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm font-bold">
            <span className="text-muted-foreground">PROGRESS</span>
            <span className="text-foreground">
              {checkedCount} / {totalCount} ITEMS
            </span>
          </div>
          <div className="w-full h-4 bg-muted border-4 border-border overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
              role="progressbar"
              aria-valuenow={progressPercentage}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${checkedCount} of ${totalCount} items checked`}
            />
          </div>
        </div>
      </div>

      {totalCount === 0 ? (
        <div className="comic-panel p-8 bg-card text-center">
          <p className="text-muted-foreground font-medium">
            No items in this shopping list yet.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {categories.map(category => {
            const categoryItems = itemsByCategory[category];
            if (!categoryItems || categoryItems.length === 0) {
              return null;
            }
            return (
              <CategorySection
                key={category}
                category={category}
                items={categoryItems}
                onItemCheck={onItemCheck}
                onItemDelete={onItemDelete}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
