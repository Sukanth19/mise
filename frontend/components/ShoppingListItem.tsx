'use client';

import { ShoppingListItem as ShoppingListItemType } from '@/types';
import { Trash2 } from 'lucide-react';

interface ShoppingListItemProps {
  item: ShoppingListItemType;
  onCheck?: (itemId: number, isChecked: boolean) => void;
  onDelete?: (itemId: number) => void;
}

export default function ShoppingListItem({ 
  item,
  onCheck,
  onDelete
}: ShoppingListItemProps) {
  const handleCheckChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onCheck?.(item.id, e.target.checked);
  };

  const handleDelete = () => {
    onDelete?.(item.id);
  };

  return (
    <div 
      className={`flex items-center gap-3 p-3 bg-card border-2 border-border transition-all ${
        item.is_checked ? 'opacity-60' : ''
      }`}
      data-testid="shopping-list-item"
    >
      <input
        type="checkbox"
        checked={item.is_checked}
        onChange={handleCheckChange}
        className="w-5 h-5 border-4 border-border rounded-none cursor-pointer accent-primary"
        aria-label={`Check ${item.ingredient_name}`}
        data-testid="item-checkbox"
      />
      
      <div className="flex-1 min-w-0">
        <div className={`font-bold text-foreground ${item.is_checked ? 'line-through' : ''}`}>
          {item.ingredient_name}
        </div>
        {item.quantity && (
          <div className="text-sm text-muted-foreground font-medium">
            {item.quantity}
          </div>
        )}
      </div>

      {item.is_custom && onDelete && (
        <button
          type="button"
          onClick={handleDelete}
          className="comic-button p-2 bg-destructive text-destructive-foreground hover:bg-destructive/80"
          aria-label={`Delete ${item.ingredient_name}`}
          data-testid="delete-button"
        >
          <Trash2 size={16} />
        </button>
      )}
    </div>
  );
}
