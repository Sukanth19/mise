'use client';

import { Recipe } from '@/types';
import { useRouter } from 'next/navigation';

interface RecipeCardProps {
  recipe: Recipe;
}

export default function RecipeCard({ recipe }: RecipeCardProps) {
  const router = useRouter();

  const handleClick = () => {
    router.push(`/recipes/${recipe.id}`);
  };

  // Construct full image URL
  const imageUrl = recipe.image_url 
    ? `http://localhost:8000${recipe.image_url}` 
    : null;

  return (
    <div
      onClick={handleClick}
      className="cursor-pointer bg-card rounded-lg shadow-md overflow-hidden transition-transform duration-300 hover:scale-105 hover:shadow-lg border border-border"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      <div className="relative w-full h-48 bg-muted">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={recipe.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground">
            No Image
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-foreground truncate">
          {recipe.title}
        </h3>
      </div>
    </div>
  );
}
