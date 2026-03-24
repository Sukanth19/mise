'use client';

import { Recipe } from '@/types';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import RatingStars from './RatingStars';
import { Check } from 'lucide-react';

interface RecipeCardProps {
  recipe: Recipe;
  index?: number;
  selectionMode?: boolean;
  isSelected?: boolean;
  onToggleSelection?: (recipeId: number) => void;
}

export default function RecipeCard({ 
  recipe, 
  index = 0,
  selectionMode = false,
  isSelected = false,
  onToggleSelection
}: RecipeCardProps) {
  const router = useRouter();

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
          <RatingStars value={0} readOnly size="sm" />
          <span className="text-xs text-muted-foreground">(No ratings yet)</span>
        </div>
      </div>
    </motion.div>
  );
}
