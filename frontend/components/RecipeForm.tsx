import React, { useState, FormEvent } from 'react';
import ImageUpload from './ImageUpload';
import { RecipeCreate, RecipeUpdate } from '@/types';
import NutritionForm, { NutritionData } from './NutritionForm';
import DietaryLabelsSelector from './DietaryLabelsSelector';
import AllergenWarnings from './AllergenWarnings';

interface RecipeFormProps {
  initialData?: RecipeUpdate & { id?: number; visibility?: string };
  onSubmit: (data: RecipeCreate | RecipeUpdate) => Promise<void>;
  submitLabel?: string;
  showNutritionSection?: boolean;
  onNutritionSubmit?: (recipeId: number, data: NutritionData) => Promise<void>;
  onDietaryLabelsSubmit?: (recipeId: number, labels: string[]) => Promise<void>;
  onAllergensSubmit?: (recipeId: number, allergens: string[]) => Promise<void>;
  onVisibilityChange?: (recipeId: number, visibility: string) => Promise<void>;
  initialNutrition?: NutritionData;
  initialDietaryLabels?: string[];
  initialAllergens?: string[];
}

export default function RecipeForm({ 
  initialData, 
  onSubmit, 
  submitLabel = 'Save Recipe',
  showNutritionSection = false,
  onNutritionSubmit,
  onDietaryLabelsSubmit,
  onAllergensSubmit,
  onVisibilityChange,
  initialNutrition,
  initialDietaryLabels = [],
  initialAllergens = [],
}: RecipeFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [imageUrl, setImageUrl] = useState(initialData?.image_url || '');
  const [ingredients, setIngredients] = useState<string[]>(
    initialData?.ingredients || ['']
  );
  const [steps, setSteps] = useState<string[]>(
    initialData?.steps || ['']
  );
  const [tags, setTags] = useState<string>(
    initialData?.tags?.join(', ') || ''
  );
  const [referenceLink, setReferenceLink] = useState(
    initialData?.reference_link || ''
  );
  const [visibility, setVisibility] = useState<string>(
    initialData?.visibility || 'private'
  );
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Nutrition state
  const [dietaryLabels, setDietaryLabels] = useState<string[]>(initialDietaryLabels);
  const [allergens, setAllergens] = useState<string[]>(initialAllergens);

  const handleVisibilityChange = async (newVisibility: string) => {
    setVisibility(newVisibility);
    if (onVisibilityChange && initialData?.id) {
      try {
        await onVisibilityChange(initialData.id, newVisibility);
      } catch (err) {
        console.error('Failed to update visibility:', err);
      }
    }
  };

  const handleAddIngredient = () => {
    setIngredients([...ingredients, '']);
  };

  const handleRemoveIngredient = (index: number) => {
    if (ingredients.length > 1) {
      setIngredients(ingredients.filter((_, i) => i !== index));
    }
  };

  const handleIngredientChange = (index: number, value: string) => {
    const newIngredients = [...ingredients];
    newIngredients[index] = value;
    setIngredients(newIngredients);
  };

  const handleAddStep = () => {
    setSteps([...steps, '']);
  };

  const handleRemoveStep = (index: number) => {
    if (steps.length > 1) {
      setSteps(steps.filter((_, i) => i !== index));
    }
  };

  const handleStepChange = (index: number, value: string) => {
    const newSteps = [...steps];
    newSteps[index] = value;
    setSteps(newSteps);
  };

  const handleImageUploaded = (url: string) => {
    setImageUrl(url);
  };

  const validateForm = (): boolean => {
    if (!title.trim()) {
      setError('Title is required');
      return false;
    }

    const nonEmptyIngredients = ingredients.filter(i => i.trim());
    if (nonEmptyIngredients.length === 0) {
      setError('At least one ingredient is required');
      return false;
    }

    const nonEmptySteps = steps.filter(s => s.trim());
    if (nonEmptySteps.length === 0) {
      setError('At least one step is required');
      return false;
    }

    setError(null);
    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const filteredIngredients = ingredients.filter(i => i.trim());
      const filteredSteps = steps.filter(s => s.trim());
      const tagArray = tags
        .split(',')
        .map(t => t.trim())
        .filter(t => t);

      const recipeData: RecipeCreate = {
        title: title.trim(),
        image_url: imageUrl || undefined,
        ingredients: filteredIngredients,
        steps: filteredSteps,
        tags: tagArray.length > 0 ? tagArray : undefined,
        reference_link: referenceLink.trim() || undefined,
      };

      await onSubmit(recipeData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save recipe');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto space-y-8">
      {error && (
        <div className="comic-border bg-destructive/10 border-destructive text-destructive px-6 py-4 font-bold animate-shake" role="alert">
          ⚠️ {error}
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block comic-label text-foreground mb-3">
          Title <span className="text-destructive">*</span>
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full comic-input px-4 py-3 text-lg font-medium"
          placeholder="Enter recipe title"
        />
      </div>

      {/* Image Upload */}
      <div>
        <label className="block comic-label text-foreground mb-3">
          Recipe Image
        </label>
        <ImageUpload 
          onImageUploaded={handleImageUploaded} 
          initialImageUrl={imageUrl}
        />
      </div>

      {/* Ingredients */}
      <div>
        <label className="block comic-label text-foreground mb-3">
          Ingredients <span className="text-destructive">*</span>
        </label>
        <div className="space-y-3">
          {ingredients.map((ingredient, index) => (
            <div key={index} className="flex gap-3 items-center">
              <input
                type="text"
                value={ingredient}
                onChange={(e) => handleIngredientChange(index, e.target.value)}
                className="flex-1 comic-input px-4 py-3 font-medium"
                placeholder={`Ingredient ${index + 1}`}
              />
              <button
                type="button"
                onClick={() => handleRemoveIngredient(index)}
                disabled={ingredients.length === 1}
                className="comic-button px-4 py-3 bg-destructive text-destructive-foreground disabled:opacity-30 disabled:cursor-not-allowed font-bold"
                aria-label={`Remove ingredient ${index + 1}`}
              >
                REMOVE
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddIngredient}
            className="comic-button px-6 py-3 bg-secondary text-secondary-foreground font-bold"
          >
            + ADD INGREDIENT
          </button>
        </div>
      </div>

      {/* Steps */}
      <div>
        <label className="block comic-label text-foreground mb-3">
          Steps <span className="text-destructive">*</span>
        </label>
        <div className="space-y-3">
          {steps.map((step, index) => (
            <div key={index} className="flex gap-3">
              <span className="flex-shrink-0 w-10 h-12 flex items-center justify-center text-foreground font-bold text-xl comic-border bg-card">
                {index + 1}
              </span>
              <textarea
                value={step}
                onChange={(e) => handleStepChange(index, e.target.value)}
                className="flex-1 comic-input px-4 py-3 font-medium resize-none"
                placeholder={`Step ${index + 1}`}
                rows={2}
              />
              <button
                type="button"
                onClick={() => handleRemoveStep(index)}
                disabled={steps.length === 1}
                className="comic-button px-4 py-3 bg-destructive text-destructive-foreground disabled:opacity-30 disabled:cursor-not-allowed font-bold"
                aria-label={`Remove step ${index + 1}`}
              >
                REMOVE
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddStep}
            className="comic-button px-6 py-3 bg-secondary text-secondary-foreground font-bold"
          >
            + ADD STEP
          </button>
        </div>
      </div>

      {/* Tags */}
      <div>
        <label htmlFor="tags" className="block comic-label text-foreground mb-3">
          Tags
        </label>
        <input
          id="tags"
          type="text"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          className="w-full comic-input px-4 py-3 font-medium"
          placeholder="Enter tags separated by commas (e.g., dinner, vegetarian, quick)"
        />
        <p className="mt-2 text-sm text-muted-foreground font-medium">Separate multiple tags with commas</p>
      </div>

      {/* Reference Link */}
      <div>
        <label htmlFor="referenceLink" className="block comic-label text-foreground mb-3">
          Reference Link
        </label>
        <input
          id="referenceLink"
          type="url"
          value={referenceLink}
          onChange={(e) => setReferenceLink(e.target.value)}
          className="w-full comic-input px-4 py-3 font-medium"
          placeholder="https://example.com/original-recipe"
        />
      </div>

      {/* Visibility Controls */}
      <div>
        <label className="block comic-label text-foreground mb-3">
          Visibility
        </label>
        <div className="space-y-3">
          <label className="flex items-center gap-3 p-4 comic-border bg-card cursor-pointer hover:bg-accent/10 transition-colors">
            <input
              type="radio"
              name="visibility"
              value="private"
              checked={visibility === 'private'}
              onChange={(e) => handleVisibilityChange(e.target.value)}
              className="w-5 h-5"
            />
            <div>
              <div className="font-bold text-foreground">🔒 Private</div>
              <div className="text-sm text-muted-foreground">Only you can see this recipe</div>
            </div>
          </label>
          
          <label className="flex items-center gap-3 p-4 comic-border bg-card cursor-pointer hover:bg-accent/10 transition-colors">
            <input
              type="radio"
              name="visibility"
              value="unlisted"
              checked={visibility === 'unlisted'}
              onChange={(e) => handleVisibilityChange(e.target.value)}
              className="w-5 h-5"
            />
            <div>
              <div className="font-bold text-foreground">🔗 Unlisted</div>
              <div className="text-sm text-muted-foreground">Anyone with the link can see this recipe</div>
            </div>
          </label>
          
          <label className="flex items-center gap-3 p-4 comic-border bg-card cursor-pointer hover:bg-accent/10 transition-colors">
            <input
              type="radio"
              name="visibility"
              value="public"
              checked={visibility === 'public'}
              onChange={(e) => handleVisibilityChange(e.target.value)}
              className="w-5 h-5"
            />
            <div>
              <div className="font-bold text-foreground">🌍 Public</div>
              <div className="text-sm text-muted-foreground">Everyone can discover this recipe</div>
            </div>
          </label>
        </div>
      </div>

      {/* Nutrition Section (only shown when editing existing recipe) */}
      {showNutritionSection && initialData?.id && (
        <div className="space-y-8 pt-8 border-t-4 border-border">
          <h2 className="text-2xl comic-heading text-foreground">NUTRITION INFORMATION</h2>
          
          {/* Nutrition Facts Form */}
          <div>
            <h3 className="text-lg font-bold uppercase text-foreground mb-4">Nutrition Facts</h3>
            <NutritionForm
              initialData={initialNutrition}
              onSubmit={async (data) => {
                if (onNutritionSubmit && initialData.id) {
                  await onNutritionSubmit(initialData.id, data);
                }
              }}
            />
          </div>

          {/* Dietary Labels */}
          <div>
            <DietaryLabelsSelector
              selectedLabels={dietaryLabels}
              onChange={async (labels) => {
                setDietaryLabels(labels);
                if (onDietaryLabelsSubmit && initialData.id) {
                  await onDietaryLabelsSubmit(initialData.id, labels);
                }
              }}
            />
          </div>

          {/* Allergen Warnings */}
          <div>
            <AllergenWarnings
              selectedAllergens={allergens}
              onChange={async (allergens) => {
                setAllergens(allergens);
                if (onAllergensSubmit && initialData.id) {
                  await onAllergensSubmit(initialData.id, allergens);
                }
              }}
              displayMode="selector"
            />
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex gap-4 pt-6">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 comic-button bg-primary text-primary-foreground py-4 px-8 text-xl disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'SAVING...' : submitLabel.toUpperCase()}
        </button>
      </div>
    </form>
  );
}
