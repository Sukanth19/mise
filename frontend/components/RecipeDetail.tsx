'use client';

import { Recipe, Collection, NutritionFacts } from '@/types';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import RatingStars from './RatingStars';
import AddToCollectionModal from './AddToCollectionModal';
import NutritionDisplay from './NutritionDisplay';
import AllergenWarnings from './AllergenWarnings';
import { apiClient } from '@/lib/api';
import PrintView from './PrintView';
import { FolderPlus } from 'lucide-react';

interface RecipeDetailProps {
  recipe: Recipe;
}

export default function RecipeDetail({ recipe }: RecipeDetailProps) {
  const [checkedIngredients, setCheckedIngredients] = useState<Set<number>>(new Set());
  const [userRating, setUserRating] = useState<number>(0);
  const [isLoadingRating, setIsLoadingRating] = useState(true);
  const [showAddToCollectionModal, setShowAddToCollectionModal] = useState(false);
  const [collections, setCollections] = useState<Collection[]>([]);
  
  // Nutrition state
  const [nutritionFacts, setNutritionFacts] = useState<NutritionFacts | null>(null);
  const [perServingNutrition, setPerServingNutrition] = useState<NutritionFacts | null>(null);
  const [servings, setServings] = useState<number>(1);
  const [dietaryLabels, setDietaryLabels] = useState<string[]>([]);
  const [allergens, setAllergens] = useState<string[]>([]);
  const [isLoadingNutrition, setIsLoadingNutrition] = useState(true);

  useEffect(() => {
    fetchUserRating();
    fetchCollections();
    fetchNutritionData();
  }, [recipe.id]);

  const fetchUserRating = async () => {
    try {
      setIsLoadingRating(true);
      const response = await apiClient<{ rating: number }>(`/api/recipes/${recipe.id}/rating`);
      setUserRating(response.rating);
    } catch (err) {
      // If 404, user hasn't rated yet - that's fine
      setUserRating(0);
    } finally {
      setIsLoadingRating(false);
    }
  };

  const fetchCollections = async () => {
    try {
      const data = await apiClient<{ collections: Collection[] }>('/api/collections');
      setCollections(data.collections);
    } catch (err) {
      console.error('Failed to fetch collections:', err);
    }
  };

  const fetchNutritionData = async () => {
    try {
      setIsLoadingNutrition(true);
      
      // Fetch nutrition facts
      const nutritionResponse = await apiClient<{ 
        nutrition_facts: NutritionFacts | null;
        per_serving: NutritionFacts | null;
      }>(`/api/recipes/${recipe.id}/nutrition`);
      
      setNutritionFacts(nutritionResponse.nutrition_facts);
      setPerServingNutrition(nutritionResponse.per_serving);
      
      // Get servings from recipe (assuming it's added to Recipe type)
      // For now, default to 1 if not available
      setServings((recipe as any).servings || 1);
      
      // Fetch dietary labels (assuming endpoint returns them)
      try {
        const recipeWithLabels = await apiClient<any>(`/api/recipes/${recipe.id}`);
        setDietaryLabels(recipeWithLabels.dietary_labels || []);
        setAllergens(recipeWithLabels.allergens || []);
      } catch (err) {
        // Labels might not be available
        setDietaryLabels([]);
        setAllergens([]);
      }
    } catch (err) {
      // Nutrition data might not exist yet
      setNutritionFacts(null);
      setPerServingNutrition(null);
    } finally {
      setIsLoadingNutrition(false);
    }
  };

  const handleAddToCollections = async (collectionIds: number[]) => {
    try {
      // Add recipe to each selected collection
      await Promise.all(
        collectionIds.map(collectionId =>
          apiClient(`/api/collections/${collectionId}/recipes`, {
            method: 'POST',
            body: JSON.stringify({ recipe_ids: [recipe.id] }),
          })
        )
      );
      alert('Recipe added to collections successfully!');
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to add to collections');
    }
  };

  const handleRatingChange = async (newRating: number) => {
    try {
      const method = userRating === 0 ? 'POST' : 'PUT';
      await apiClient(`/api/recipes/${recipe.id}/rating`, {
        method,
        body: JSON.stringify({ rating: newRating }),
      });
      setUserRating(newRating);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save rating');
      // Revert on error
      fetchUserRating();
    }
  };

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
    <>
      {/* Print View Component */}
      <div className="hidden print:block">
        <PrintView recipe={recipe} />
      </div>

      {/* Regular View */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="max-w-4xl mx-auto comic-panel overflow-hidden print:hidden"
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

        {/* Rating */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
          className="mb-6"
        >
          <div className="flex items-center gap-3">
            <span className="text-sm font-bold text-muted-foreground uppercase">Your Rating:</span>
            {isLoadingRating ? (
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="w-6 h-6 bg-muted animate-pulse rounded" />
                ))}
              </div>
            ) : (
              <RatingStars value={userRating} onChange={handleRatingChange} size="md" />
            )}
          </div>
        </motion.div>

        {/* Allergen Warnings - Prominent Display */}
        {!isLoadingNutrition && allergens.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.38 }}
            className="mb-6"
          >
            <AllergenWarnings
              selectedAllergens={allergens}
              displayMode="display"
            />
          </motion.div>
        )}

        {/* Dietary Labels */}
        {!isLoadingNutrition && dietaryLabels.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.39 }}
            className="mb-6"
          >
            <div className="flex flex-wrap gap-2">
              {dietaryLabels.map((label) => (
                <span
                  key={label}
                  className="px-3 py-1 comic-border bg-secondary/20 text-secondary-foreground text-sm font-bold uppercase"
                >
                  {label}
                </span>
              ))}
            </div>
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

        {/* Nutrition Display */}
        {!isLoadingNutrition && (nutritionFacts || perServingNutrition) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.75 }}
            className="mb-8"
          >
            <NutritionDisplay
              nutritionFacts={nutritionFacts}
              perServing={perServingNutrition}
              servings={servings}
              showPerServing={true}
            />
          </motion.div>
        )}

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

        {/* Print Button */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.85 }}
          className="mt-6 flex gap-4"
        >
          <button
            type="button"
            onClick={() => window.print()}
            className="comic-button px-6 py-3 bg-primary text-primary-foreground"
            aria-label="Print recipe"
          >
            🖨️ PRINT RECIPE
          </button>
          <button
            type="button"
            onClick={() => setShowAddToCollectionModal(true)}
            className="comic-button px-6 py-3 bg-secondary text-secondary-foreground flex items-center gap-2"
            aria-label="Add to collection"
          >
            <FolderPlus size={20} strokeWidth={2.5} />
            ADD TO COLLECTION
          </button>
        </motion.div>
      </div>
    </motion.div>

    {/* Add to Collection Modal */}
    <AddToCollectionModal
      isOpen={showAddToCollectionModal}
      onClose={() => setShowAddToCollectionModal(false)}
      onSubmit={handleAddToCollections}
      collections={collections}
      recipeTitle={recipe.title}
    />
    </>
  );
}
