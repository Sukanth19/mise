'use client';

import { useState } from 'react';
import { ShoppingListItem as ShoppingListItemType } from '@/types';
import { ChevronDown, ChevronRight } from 'lucide-react';
import ShoppingListItem from './ShoppingListItem';

interface CategorySectionProps {
  category: 'produce' | 'dairy' | 'meat' | 'pantry' | 'other';
  items: ShoppingListItemType[];
  onItemCheck?: (itemId: number, isChecked: boolean) => void;
  onItemDelete?: (itemId: number) => void;
}

const categoryLabels: Record<string, string> = {
  produce: 'Produce',
  dairy: 'Dairy',
  meat: 'Meat & Seafood',
  pantry: 'Pantry',
  other: 'Other',
};

export default function CategorySection({ 
  category,
  items,
  onItemCheck,
  onItemDelete
}: CategorySectionProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const categoryLabel = categoryLabels[category] || category;

  return (
    <div className="comic-panel bg-card overflow-hidden">
      <button
        type="button"
        onClick={toggleExpanded}
        className="w-full p-4 flex items-center justify-between bg-muted hover:bg-muted/80 transition-colors border-b-4 border-border"
        aria-expanded={isExpanded}
        aria-controls={`category-${category}-items`}
        data-testid="category-header"
      >
        <div className="flex items-center gap-3">
          {isExpanded ? (
            <ChevronDown size={24} strokeWidth={3} className="text-foreground" />
          ) : (
            <ChevronRight size={24} strokeWidth={3} className="text-foreground" />
          )}
          <h2 className="text-xl font-black text-foreground uppercase tracking-wide">
            {categoryLabel}
          </h2>
          <span className="text-sm font-bold text-muted-foreground">
            ({items.length})
          </span>
        </div>
      </button>

      {isExpanded && (
        <div 
          id={`category-${category}-items`}
          className="divide-y-2 divide-border"
          data-testid="category-items"
        >
          {items.map(item => (
            <ShoppingListItem
              key={item.id}
              item={item}
              onCheck={onItemCheck}
              onDelete={onItemDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
