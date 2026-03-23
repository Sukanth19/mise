'use client';

import { Recipe } from '@/types';
import { useState } from 'react';
import { motion } from 'framer-motion';

interface RecipeDetailProps {
  recipe: Recipe;
}

export default function RecipeDetail({ recipe }: RecipeDetailProps) {
  const [checkedIngredients, setCheckedIngredients] = useState<Set<number>>(new Set());

  const toggleIngredient = (index: number) => {
    setCheckedIngredients((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  // Construct full image URL
  const imageUrl = recipe.image_url 
    ? `http://localhost:8000${recipe.image_url}` 
    : null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto comic-panel overflow-hidden"
    >
      {/* Image */}
      {imageUrl && (
        <div className="w-full h-64 md:h-96 bg-muted overflow-hidden">
          <motion.img
            initial={{ scale: 1.1 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.6 }}
            src={imageUrl}
            alt={recipe.title}
            className="w-full h-full object-cover recipe-image"
          />
        </div>
      )}

      <div className="p-6 md:p-8">
        {/* Title */}
        <motion.h1 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="text-3xl comic-heading text-foreground mb-4"
        >
          {recipe.title}
        </motion.h1>

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex flex-wrap gap-2 mb-6"
          >
            {recipe.tags.map((tag, index) => (
              <motion.span
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 + index * 0.05 }}
                className="px-3 py-1 comic-border bg-primary/10 text-primary text-sm font-bold uppercase"
              >
                {tag}
              </motion.span>
            ))}
          </motion.div>
        )}

        {/* Ingredients */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <h2 className="text-2xl comic-heading text-foreground mb-4">Ingredients</h2>
          <ul className="space-y-2">
            {recipe.ingredients.map((ingredient, index) => (
              <motion.li 
                key={index} 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.05 }}
                className="flex items-start"
              >
                <input
                  type="checkbox"
                  id={`ingredient-${index}`}
                  checked={checkedIngredients.has(index)}
                  onChange={() => toggleIngredient(index)}
                  className="mt-1 mr-3 h-5 w-5 accent-primary rounded focus:ring-2 focus:ring-ring cursor-pointer"
                />
                <label
                  htmlFor={`ingredient-${index}`}
                  className={`flex-1 cursor-pointer font-bold transition-all duration-200 ${
                    checkedIngredients.has(index) ? 'line-through text-muted-foreground opacity-60' : 'text-foreground'
                  }`}
                >
                  {ingredient}
                </label>
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Steps */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mb-8"
        >
          <h2 className="text-2xl comic-heading text-foreground mb-4">Instructions</h2>
          <ol className="space-y-4">
            {recipe.steps.map((step, index) => (
              <motion.li 
                key={index} 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.1 }}
                className="flex"
              >
                <span className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground flex items-center justify-center font-black mr-4 comic-border">
                  {index + 1}
                </span>
                <p className="flex-1 text-foreground pt-1 font-medium">{step}</p>
              </motion.li>
            ))}
          </ol>
        </motion.div>

        {/* Reference Link */}
        {recipe.reference_link && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="mt-6"
          >
            <a
              href={recipe.reference_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block comic-button px-6 py-3 bg-success text-white"
            >
              VIEW ORIGINAL RECIPE
            </a>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
