'use client';

import { Collection } from '@/types';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Pencil, Trash2, Folder } from 'lucide-react';

interface CollectionCardProps {
  collection: Collection;
  index?: number;
  onEdit?: (collection: Collection) => void;
  onDelete?: (collection: Collection) => void;
}

export default function CollectionCard({ 
  collection, 
  index = 0,
  onEdit,
  onDelete 
}: CollectionCardProps) {
  const router = useRouter();

  const handleClick = () => {
    router.push(`/collections/${collection.id}`);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(collection);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(collection);
  };

  // Construct full image URL
  const imageUrl = collection.cover_image_url 
    ? `http://localhost:8000${collection.cover_image_url}` 
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.4, 
        delay: index * 0.08,
        ease: [0.4, 0, 0.2, 1]
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
      aria-label={`Collection: ${collection.name}`}
    >
      <div className="relative w-full h-48 bg-muted border-b-4 border-border overflow-hidden">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={collection.name}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground">
            <Folder size={64} strokeWidth={3} />
          </div>
        )}
      </div>
      <div className="p-4 bg-card">
        <h3 className="text-lg font-black text-foreground truncate uppercase tracking-wide mb-2">
          {collection.name}
        </h3>
        {collection.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3 font-medium">
            {collection.description}
          </p>
        )}
        <div className="flex items-center justify-between">
          <span className="text-sm font-bold text-muted-foreground">
            {collection.recipe_count || 0} RECIPES
          </span>
          <div className="flex gap-2">
            {onEdit && (
              <button
                onClick={handleEdit}
                className="comic-button p-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
                aria-label={`Edit ${collection.name}`}
                data-testid="edit-button"
              >
                <Pencil size={16} />
              </button>
            )}
            {onDelete && (
              <button
                onClick={handleDelete}
                className="comic-button p-2 bg-destructive text-destructive-foreground hover:bg-destructive/80"
                aria-label={`Delete ${collection.name}`}
                data-testid="delete-button"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
