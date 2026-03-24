'use client';

import { Recipe } from '@/types';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import RatingStars from './RatingStars';
import { Check, Star, Eye, EyeOff, Link } from 'lucide-react';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

interface RecipeCardProps {
  recipe: Recipe;
  index?: number;
  selectionMode?: boolean;
  isSelected?: boolean;
  onToggleSelection?: (recipeId: number) => void;
  onFavoriteToggle?: (recipeId: number, isFavorite: boolean) => void;
}

export default function RecipeCard({ 
  recipe, 
  index = 0,
  selectionMode = false,
  isSelected = false,
  onToggleSelection,
  onFavoriteToggle
}: RecipeCardProps) {
  const router = useRouter();
  const [isFavorite, setIsFavorite] = useState((recipe as any).is_favorite || false);
  const [averageRating, setAverageRating] = useState(0);
  const [isLoadingRating, setIsLoadingRating] = useState(true);

  useEffect(() => {
    // Fetch average rating for the recipe
    fetchAverageRating();
  }, [recipe.id]);

  const fetchAverageRating = async () => {
    try {
      setIsLoadingRating(true);
      // This would need a backend endpoint to get average rating
      // For now, we'll just set it to 0
      setAverageRating(0);
    } catch (err) {
      setAverageRating(0);
    } finally {
      setIsLoadingRating(false);
    }
  };

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient(`/api/recipes/${recipe.id}/favorite`, {
        method: 'PATCH',
        body: JSON.stringify({ is_favorite: !isFavorite }),
      });
      setIsFavorite(!isFavorite);
      if (onFavoriteToggle) {
        onFavoriteToggle(recipe.id, !isFavorite);
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    }
  };

  const handleClick = () => {
    if (selectionMode && onToggleSelection) {
      onToggleSelection(recipe.id);
    } else {
      router.push(`/recipes/${recipe.id}`);
    }
  };

  const handleCheckboxClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onToggleSelection) {
      onToggleSelection(recipe.id);
    }
  };

  // Construct full image URL
  const imageUrl = recipe.image_url 
    ? `http://localhost:8000${recipe.image_url}` 
    : null;

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
      className={`cursor-pointer comic-panel rounded-none overflow-hidden transition-all duration-100 hover:translate-x-1 hover:translate-y-1 hover:shadow-none group ${
        isSelected ? 'ring-4 ring-primary' : ''
      }`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      <div className="relative w-full h-48 bg-muted border-b-4 border-border overflow-hidden">
        {selectionMode && (
          <div 
            className="absolute top-2 left-2 z-10"
            onClick={handleCheckboxClick}
          >
            <div className={`w-8 h-8 comic-border flex items-center justify-center cursor-pointer ${
              isSelected ? 'bg-primary text-primary-foreground' : 'bg-background'
            }`}>
              {isSelected && <Check size={20} strokeWidth={3} />}
            </div>
          </div>
        )}
        
        {/* Favorite Star */}
        {!selectionMode && (
          <button
            type="button"
            onClick={handleFavoriteClick}
            className="absolute top-2 right-2 z-10 w-10 h-10 comic-border bg-background/90 hover:bg-background flex items-center justify-center transition-colors"
            aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Star
              size={20}
              strokeWidth={2.5}
              className={isFavorite ? 'fill-warning text-warning' : 'text-muted-foreground'}
            />
          </button>
        )}

        {/* Visibility Indicator */}
        {recipe.visibility && recipe.visibility !== 'private' && (
          <div className="absolute top-2 left-2 z-10 px-2 py-1 comic-border bg-background/90 flex items-center gap-1">
            {recipe.visibility === 'public' ? (
              <>
                <Eye size={14} strokeWidth={2.5} className="text-success" />
                <span className="text-xs font-bold text-success uppercase">Public</span>
              </>
            ) : (
              <>
                <Link size={14} strokeWidth={2.5} className="text-muted-foreground" />
                <span className="text-xs font-bold text-muted-foreground uppercase">Unlisted</span>
              </>
            )}
          </div>
        )}

        {imageUrl ? (
          <img
            src={imageUrl}
            alt={recipe.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110 recipe-image"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground font-black text-xl">
            NO IMAGE
          </div>
        )}
      </div>
      <div className="p-4 bg-card">
        <h3 className="text-lg font-black text-foreground truncate uppercase tracking-wide mb-2">
          {recipe.title}
        </h3>
        <div className="flex items-center gap-2">
          {isLoadingRating ? (
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="w-4 h-4 bg-muted animate-pulse rounded" />
              ))}
            </div>
          ) : (
            <>
              <RatingStars value={averageRating} readOnly size="sm" />
              <span className="text-xs text-muted-foreground">
                {averageRating > 0 ? `(${averageRating.toFixed(1)})` : '(No ratings yet)'}
              </span>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
}
