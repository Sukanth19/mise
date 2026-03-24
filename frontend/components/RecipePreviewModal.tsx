'use client';

import { Recipe } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

interface RecipePreviewModalProps {
  recipe: Recipe | null;
  isOpen: boolean;
  onClose: () => void;
  onDelete?: (recipeId: number) => void;
}

export default function RecipePreviewModal({
  recipe,
  isOpen,
  onClose,
  onDelete,
}: RecipePreviewModalProps) {
  const router = useRouter();

  if (!recipe) return null;

  const imageUrl = recipe.image_url 
    ? `http://localhost:8000${recipe.image_url}` 
    : null;

  const handleEdit = () => {
    router.push(`/recipes/${recipe.id}/edit`);
    onClose();
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete(recipe.id);
    }
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop with fade animation */}
          <motion.div
            className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />

          {/* Modal with scale and fade animation */}
          <motion.div
            className="relative comic-panel max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ type: 'spring', duration: 0.4 }}
          >
            {/* Close button */}
            <button
              type="button"
              onClick={onClose}
              className="absolute top-4 right-4 text-2xl text-muted-foreground hover:text-foreground transition-colors z-10"
              aria-label="Close preview"
            >
              ✕
            </button>

            {/* Image */}
            {imageUrl && (
              <div className="w-full h-48 md:h-64 bg-muted overflow-hidden">
                <img
                  src={imageUrl}
                  alt={recipe.title}
                  className="w-full h-full object-cover"
                />
              </div>
            )}

            <div className="p-6">
              {/* Title */}
              <h2 className="text-2xl comic-heading text-foreground mb-4">
                {recipe.title}
              </h2>

              {/* Tags */}
              {recipe.tags && recipe.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {recipe.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 comic-border bg-primary/10 text-primary text-sm font-bold uppercase"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Ingredients */}
              <div className="mb-6">
                <h3 className="text-xl comic-heading text-foreground mb-3">Ingredients</h3>
                <ul className="space-y-2">
                  {recipe.ingredients.map((ingredient, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2 text-primary font-bold">•</span>
                      <span className="flex-1 font-medium">{ingredient}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Steps */}
              <div className="mb-6">
                <h3 className="text-xl comic-heading text-foreground mb-3">Instructions</h3>
                <ol className="space-y-3">
                  {recipe.steps.map((step, index) => (
                    <li key={index} className="flex">
                      <span className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground flex items-center justify-center font-black mr-3 comic-border text-sm">
                        {index + 1}
                      </span>
                      <p className="flex-1 text-foreground font-medium">{step}</p>
                    </li>
                  ))}
                </ol>
              </div>

              {/* Reference Link */}
              {recipe.reference_link && (
                <div className="mb-6">
                  <a
                    href={recipe.reference_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline font-bold text-sm"
                  >
                    View Original Recipe →
                  </a>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex gap-3 justify-end pt-4 border-t border-border">
                <button
                  type="button"
                  onClick={handleEdit}
                  className="comic-button px-6 py-3 bg-primary text-primary-foreground"
                >
                  EDIT
                </button>
                {onDelete && (
                  <button
                    type="button"
                    onClick={handleDelete}
                    className="comic-button px-6 py-3 bg-destructive text-destructive-foreground"
                  >
                    DELETE
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
