'use client';

import { Recipe } from '@/types';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, Search } from 'lucide-react';

interface AddRecipesToCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (recipeIds: number[]) => Promise<void>;
  availableRecipes: Recipe[];
  collectionName?: string;
}

export default function AddRecipesToCollectionModal({
  isOpen,
  onClose,
  onSubmit,
  availableRecipes,
  collectionName
}: AddRecipesToCollectionModalProps) {
  const [selectedRecipeIds, setSelectedRecipeIds] = useState<Set<number>>(new Set());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setSelectedRecipeIds(new Set());
      setError(null);
      setSearchQuery('');
    }
  }, [isOpen]);

  const handleToggleRecipe = (recipeId: number) => {
    setSelectedRecipeIds(prev => {
      const newSelected = new Set(prev);
      if (newSelected.has(recipeId)) {
        newSelected.delete(recipeId);
      } else {
        newSelected.add(recipeId);
      }
      return newSelected;
    });
  };

  const handleSubmit = async () => {
    if (selectedRecipeIds.size === 0) {
      setError('Please select at least one recipe');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(Array.from(selectedRecipeIds));
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add recipes');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Filter recipes based on search query
  const filteredRecipes = availableRecipes.filter(recipe =>
    recipe.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        key="modal-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={handleBackdropClick}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <motion.div
          key="modal-content"
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
              Add Recipes
            </h2>
            <button
              type="button"
              onClick={onClose}
              className="comic-button p-2 bg-secondary text-secondary-foreground"
              aria-label="Close modal"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {collectionName && (
              <p className="text-sm text-muted-foreground font-medium mb-4">
                Adding to: <span className="font-bold">{collectionName}</span>
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

            {/* Search Bar */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={20} />
              <input
                type="text"
                placeholder="Search recipes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 comic-input"
              />
            </div>

            {availableRecipes.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🍳</div>
                <p className="text-muted-foreground font-bold">No recipes available</p>
                <p className="text-muted-foreground text-sm mt-2">
                  All your recipes are already in this collection
                </p>
              </div>
            ) : filteredRecipes.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-2">🔍</div>
                <p className="text-muted-foreground font-bold">No recipes found</p>
                <p className="text-muted-foreground text-sm mt-2">
                  Try a different search term
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredRecipes.map(recipe => {
                  const isSelected = selectedRecipeIds.has(recipe.id);
                  const imageUrl = recipe.image_url 
                    ? `http://localhost:8000${recipe.image_url}` 
                    : null;
                  
                  return (
                    <button
                      key={recipe.id}
                      type="button"
                      onClick={() => handleToggleRecipe(recipe.id)}
                      className={`
                        w-full flex items-center gap-3 p-4 comic-border rounded-none
                        transition-all duration-100
                        ${isSelected 
                          ? 'bg-primary text-primary-foreground border-primary' 
                          : 'bg-card hover:bg-muted'
                        }
                      `}
                      aria-label={`${isSelected ? 'Deselect' : 'Select'} ${recipe.title}`}
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
                      
                      {imageUrl && (
                        <div className="w-12 h-12 flex-shrink-0 overflow-hidden comic-border">
                          <img
                            src={imageUrl}
                            alt={recipe.title}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      
                      <div className="flex-1 text-left">
                        <div className="font-bold uppercase tracking-wide text-sm">
                          {recipe.title}
                        </div>
                        {recipe.tags && recipe.tags.length > 0 && (
                          <div className="text-xs opacity-70 mt-1">
                            {recipe.tags.slice(0, 3).join(', ')}
                          </div>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          {availableRecipes.length > 0 && (
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
                disabled={isSubmitting || selectedRecipeIds.size === 0}
                className="flex-1 comic-button bg-primary text-primary-foreground py-3 px-6 font-bold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting 
                  ? 'ADDING...' 
                  : `ADD ${selectedRecipeIds.size} RECIPE${selectedRecipeIds.size !== 1 ? 'S' : ''}`
                }
              </button>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
