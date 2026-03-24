'use client';

import { Collection } from '@/types';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Folder, Check } from 'lucide-react';

interface AddToCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (collectionIds: number[]) => Promise<void>;
  collections: Collection[];
  recipeTitle?: string;
  initialSelectedIds?: number[];
}

export default function AddToCollectionModal({
  isOpen,
  onClose,
  onSubmit,
  collections,
  recipeTitle,
  initialSelectedIds = []
}: AddToCollectionModalProps) {
  const [selectedCollectionIds, setSelectedCollectionIds] = useState<Set<number>>(
    new Set(initialSelectedIds)
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedCollectionIds(new Set(initialSelectedIds));
  }, [initialSelectedIds, isOpen]);

  const handleToggleCollection = (collectionId: number) => {
    const newSelected = new Set(selectedCollectionIds);
    if (newSelected.has(collectionId)) {
      newSelected.delete(collectionId);
    } else {
      newSelected.add(collectionId);
    }
    setSelectedCollectionIds(newSelected);
  };

  const handleSubmit = async () => {
    if (selectedCollectionIds.size === 0) {
      setError('Please select at least one collection');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(Array.from(selectedCollectionIds));
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add to collections');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={handleBackdropClick}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
          className="comic-panel bg-card w-full max-w-2xl max-h-[80vh] flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b-4 border-border">
            <h2 id="modal-title" className="text-2xl font-black uppercase tracking-wide">
              Add to Collections
            </h2>
            <button
              onClick={onClose}
              className="comic-button p-2 bg-secondary text-secondary-foreground"
              aria-label="Close modal"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {recipeTitle && (
              <p className="text-sm text-muted-foreground font-medium mb-4">
                Adding: <span className="font-bold">{recipeTitle}</span>
              </p>
            )}

            {error && (
              <div 
                className="comic-border bg-destructive/10 border-destructive text-destructive px-4 py-3 font-bold mb-4" 
                role="alert"
              >
                ⚠️ {error}
              </div>
            )}

            {collections.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">📁</div>
                <p className="text-muted-foreground font-bold">No collections yet</p>
                <p className="text-muted-foreground text-sm mt-2">
                  Create a collection first to organize your recipes
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {collections.map(collection => {
                  const isSelected = selectedCollectionIds.has(collection.id);
                  const nestingPaddingClass = collection.nesting_level === 0 ? '' : 
                    collection.nesting_level === 1 ? 'pl-6' : 
                    collection.nesting_level === 2 ? 'pl-12' : 'pl-[4.5rem]';
                  
                  return (
                    <button
                      key={collection.id}
                      type="button"
                      onClick={() => handleToggleCollection(collection.id)}
                      className={`
                        w-full flex items-center gap-3 p-4 comic-border rounded-none
                        transition-all duration-100
                        ${isSelected 
                          ? 'bg-primary text-primary-foreground border-primary' 
                          : 'bg-card hover:bg-muted'
                        }
                      `}
                      aria-label={`${isSelected ? 'Remove from' : 'Add to'} ${collection.name}`}
                    >
                      <div className="flex-shrink-0">
                        {isSelected ? (
                          <div className="w-6 h-6 bg-primary-foreground text-primary flex items-center justify-center comic-border">
                            <Check size={16} strokeWidth={3} />
                          </div>
                        ) : (
                          <div className="w-6 h-6 bg-background comic-border" />
                        )}
                      </div>
                      
                      <Folder 
                        size={20} 
                        strokeWidth={2.5} 
                        className="flex-shrink-0" 
                      />
                      
                      <div className="flex-1 text-left">
                        <div className={`font-bold uppercase tracking-wide text-sm ${nestingPaddingClass}`}>
                          {collection.name}
                        </div>
                        {collection.description && (
                          <div className="text-xs opacity-70 mt-1 line-clamp-1">
                            {collection.description}
                          </div>
                        )}
                      </div>
                      
                      <span className="text-xs opacity-70 font-bold">
                        {collection.recipe_count || 0} recipes
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          {collections.length > 0 && (
            <div className="flex gap-4 p-6 border-t-4 border-border">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 comic-button bg-secondary text-secondary-foreground py-3 px-6 font-bold"
                disabled={isSubmitting}
              >
                CANCEL
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting || selectedCollectionIds.size === 0}
                className="flex-1 comic-button bg-primary text-primary-foreground py-3 px-6 font-bold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting 
                  ? 'ADDING...' 
                  : `ADD TO ${selectedCollectionIds.size} COLLECTION${selectedCollectionIds.size !== 1 ? 'S' : ''}`
                }
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
