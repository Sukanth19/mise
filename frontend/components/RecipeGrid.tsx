'use client';

import { Recipe } from '@/types';
import RecipeCard from './RecipeCard';
import { motion, AnimatePresence } from 'framer-motion';

interface RecipeGridProps {
  recipes: Recipe[];
  selectionMode?: boolean;
  selectedRecipeIds?: Set<number>;
  onToggleSelection?: (recipeId: number) => void;
}

export default function RecipeGrid({ 
  recipes, 
  selectionMode = false,
  selectedRecipeIds = new Set(),
  onToggleSelection
}: RecipeGridProps) {
  if (recipes.length === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12 comic-panel max-w-md mx-auto"
      >
        <div className="text-6xl mb-4">🍳</div>
        <p className="text-muted-foreground font-bold text-lg">No recipes found</p>
        <p className="text-muted-foreground text-sm mt-2">Try adjusting your search or add a new recipe</p>
      </motion.div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <AnimatePresence mode="popLayout">
        {recipes.map((recipe, index) => (
          <RecipeCard 
            key={recipe.id} 
            recipe={recipe} 
            index={index}
            selectionMode={selectionMode}
            isSelected={selectedRecipeIds.has(recipe.id)}
            onToggleSelection={onToggleSelection}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
