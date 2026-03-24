'use client';

import { MealPlan } from '@/types';
import { motion } from 'framer-motion';
import { Trash2, GripVertical } from 'lucide-react';
import { useState } from 'react';

interface MealPlanCardProps {
  mealPlan: MealPlan;
  onDelete: (mealPlanId: number) => void;
  onDragStart?: (mealPlan: MealPlan) => void;
  onDragEnd?: () => void;
}

export default function MealPlanCard({
  mealPlan,
  onDelete,
  onDragStart,
  onDragEnd,
}: MealPlanCardProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragStart = (e: React.DragEvent) => {
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('application/json', JSON.stringify({
      type: 'meal-plan',
      mealPlanId: mealPlan.id,
      recipeId: mealPlan.recipe_id,
    }));
    onDragStart?.(mealPlan);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
    onDragEnd?.();
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(mealPlan.id);
  };

  // Construct full image URL
  const imageUrl = mealPlan.recipe?.image_url
    ? `http://localhost:8000${mealPlan.recipe.image_url}`
    : null;

  return (
    <motion.div
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: isDragging ? 0.5 : 1, scale: isDragging ? 0.95 : 1 }}
      transition={{ duration: 0.2 }}
      className={`comic-border bg-card p-2 cursor-move group relative ${
        isDragging ? 'shadow-lg' : ''
      }`}
    >
      {/* Drag handle */}
      <div className="absolute top-1 left-1 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
        <GripVertical size={16} />
      </div>

      {/* Delete button */}
      <button
        type="button"
        onClick={handleDelete}
        className="absolute top-1 right-1 comic-button p-1 bg-destructive text-destructive-foreground hover:bg-destructive/80 opacity-0 group-hover:opacity-100 transition-opacity"
        aria-label="Delete meal plan"
      >
        <Trash2 size={14} />
      </button>

      <div className="flex items-center gap-2 mt-4">
        {/* Recipe thumbnail */}
        {imageUrl ? (
          <div className="w-12 h-12 flex-shrink-0 comic-border overflow-hidden">
            <img
              src={imageUrl}
              alt={mealPlan.recipe?.title || 'Recipe'}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="w-12 h-12 flex-shrink-0 comic-border bg-muted flex items-center justify-center">
            <span className="text-xs font-black text-muted-foreground">NO IMG</span>
          </div>
        )}

        {/* Recipe title */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-bold truncate" title={mealPlan.recipe?.title}>
            {mealPlan.recipe?.title || 'Unknown Recipe'}
          </p>
          <p className="text-xs text-muted-foreground uppercase font-bold">
            {mealPlan.meal_time}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
