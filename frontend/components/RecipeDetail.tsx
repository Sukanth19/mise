'use client';

import { Recipe } from '@/types';
import { useState } from 'react';

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
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md overflow-hidden">
      {/* Image */}
      {imageUrl && (
        <div className="w-full h-64 md:h-96 bg-gray-200">
          <img
            src={imageUrl}
            alt={recipe.title}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      <div className="p-6 md:p-8">
        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{recipe.title}</h1>

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-6">
            {recipe.tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Ingredients */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Ingredients</h2>
          <ul className="space-y-2">
            {recipe.ingredients.map((ingredient, index) => (
              <li key={index} className="flex items-start">
                <input
                  type="checkbox"
                  id={`ingredient-${index}`}
                  checked={checkedIngredients.has(index)}
                  onChange={() => toggleIngredient(index)}
                  className="mt-1 mr-3 h-5 w-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <label
                  htmlFor={`ingredient-${index}`}
                  className={`flex-1 cursor-pointer ${
                    checkedIngredients.has(index) ? 'line-through text-gray-500' : 'text-gray-700'
                  }`}
                >
                  {ingredient}
                </label>
              </li>
            ))}
          </ul>
        </div>

        {/* Steps */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Instructions</h2>
          <ol className="space-y-4">
            {recipe.steps.map((step, index) => (
              <li key={index} className="flex">
                <span className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold mr-4">
                  {index + 1}
                </span>
                <p className="flex-1 text-gray-700 pt-1">{step}</p>
              </li>
            ))}
          </ol>
        </div>

        {/* Reference Link */}
        {recipe.reference_link && (
          <div className="mt-6">
            <a
              href={recipe.reference_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 hover:shadow-lg hover:scale-105 transition-all duration-200"
            >
              View Original Recipe
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
