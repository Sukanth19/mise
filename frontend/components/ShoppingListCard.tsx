'use client';

import { ShoppingList } from '@/types';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Eye, Share2, Trash2, ShoppingCart } from 'lucide-react';

interface ShoppingListCardProps {
  shoppingList: ShoppingList;
  index?: number;
  onShare?: (shoppingList: ShoppingList) => void;
  onDelete?: (shoppingList: ShoppingList) => void;
}

export default function ShoppingListCard({ 
  shoppingList, 
  index = 0,
  onShare,
  onDelete 
}: ShoppingListCardProps) {
  const router = useRouter();

  const handleClick = () => {
    router.push(`/shopping-lists/${shoppingList.id}`);
  };

  const handleShare = (e: React.MouseEvent) => {
    e.stopPropagation();
    onShare?.(shoppingList);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(shoppingList);
  };

  const itemCount = shoppingList.items?.length || 0;
  const createdDate = new Date(shoppingList.created_at).toLocaleDateString();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.3, 
        delay: index * 0.05,
        ease: 'easeOut'
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={handleClick}
      className="cursor-pointer comic-panel rounded-none overflow-hidden transition-all duration-100 hover:translate-x-1 hover:translate-y-1 hover:shadow-none group"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
      aria-label={`Shopping list: ${shoppingList.name}`}
    >
      <div className="relative w-full h-32 bg-muted border-b-4 border-border overflow-hidden">
        <div className="w-full h-full flex items-center justify-center text-muted-foreground">
          <ShoppingCart size={64} strokeWidth={3} />
        </div>
      </div>
      <div className="p-4 bg-card">
        <h3 className="text-lg font-black text-foreground truncate uppercase tracking-wide mb-2">
          {shoppingList.name}
        </h3>
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-bold text-muted-foreground">
            {itemCount} ITEMS
          </span>
          <span className="text-xs font-medium text-muted-foreground">
            {createdDate}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleClick}
            className="comic-button flex-1 p-2 bg-primary text-primary-foreground hover:bg-primary/80 flex items-center justify-center gap-2"
            aria-label={`View ${shoppingList.name}`}
            data-testid="view-button"
          >
            <Eye size={16} />
            <span className="text-sm font-bold">VIEW</span>
          </button>
          {onShare && (
            <button
              type="button"
              onClick={handleShare}
              className="comic-button p-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
              aria-label={`Share ${shoppingList.name}`}
              data-testid="share-button"
            >
              <Share2 size={16} />
            </button>
          )}
          {onDelete && (
            <button
              type="button"
              onClick={handleDelete}
              className="comic-button p-2 bg-destructive text-destructive-foreground hover:bg-destructive/80"
              aria-label={`Delete ${shoppingList.name}`}
              data-testid="delete-button"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
