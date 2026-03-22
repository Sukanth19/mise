import React, { useState, FormEvent } from 'react';
import ImageUpload from './ImageUpload';
import { RecipeCreate, RecipeUpdate } from '@/types';

interface RecipeFormProps {
  initialData?: RecipeUpdate & { id?: number };
  onSubmit: (data: RecipeCreate | RecipeUpdate) => Promise<void>;
  submitLabel?: string;
}

export default function RecipeForm({ 
  initialData, 
  onSubmit, 
  submitLabel = 'Save Recipe' 
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
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

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
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto space-y-6">
      {error && (
        <div className="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded" role="alert">
          {error}
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-foreground mb-1">
          Title <span className="text-destructive">*</span>
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="Enter recipe title"
        />
      </div>

      {/* Image Upload */}
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">
          Recipe Image
        </label>
        <ImageUpload 
          onImageUploaded={handleImageUploaded} 
          initialImageUrl={imageUrl}
        />
      </div>

      {/* Ingredients */}
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">
          Ingredients <span className="text-destructive">*</span>
        </label>
        <div className="space-y-2">
          {ingredients.map((ingredient, index) => (
            <div key={index} className="flex gap-2">
              <input
                type="text"
                value={ingredient}
                onChange={(e) => handleIngredientChange(index, e.target.value)}
                className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder={`Ingredient ${index + 1}`}
              />
              <button
                type="button"
                onClick={() => handleRemoveIngredient(index)}
                disabled={ingredients.length === 1}
                className="px-3 py-2 text-destructive hover:opacity-80 hover:scale-110 disabled:text-muted-foreground disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
                aria-label={`Remove ingredient ${index + 1}`}
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddIngredient}
            className="text-primary hover:opacity-80 hover:scale-105 text-sm font-medium transition-all duration-200"
          >
            + Add Ingredient
          </button>
        </div>
      </div>

      {/* Steps */}
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">
          Steps <span className="text-destructive">*</span>
        </label>
        <div className="space-y-2">
          {steps.map((step, index) => (
            <div key={index} className="flex gap-2">
              <span className="flex-shrink-0 w-8 h-10 flex items-center justify-center text-muted-foreground font-medium">
                {index + 1}.
              </span>
              <textarea
                value={step}
                onChange={(e) => handleStepChange(index, e.target.value)}
                className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                placeholder={`Step ${index + 1}`}
                rows={2}
              />
              <button
                type="button"
                onClick={() => handleRemoveStep(index)}
                disabled={steps.length === 1}
                className="px-3 py-2 text-destructive hover:opacity-80 hover:scale-110 disabled:text-muted-foreground disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
                aria-label={`Remove step ${index + 1}`}
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddStep}
            className="text-primary hover:opacity-80 hover:scale-105 text-sm font-medium transition-all duration-200"
          >
            + Add Step
          </button>
        </div>
      </div>

      {/* Tags */}
      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-foreground mb-1">
          Tags
        </label>
        <input
          id="tags"
          type="text"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="Enter tags separated by commas (e.g., dinner, vegetarian, quick)"
        />
        <p className="mt-1 text-xs text-muted-foreground">Separate multiple tags with commas</p>
      </div>

      {/* Reference Link */}
      <div>
        <label htmlFor="referenceLink" className="block text-sm font-medium text-foreground mb-1">
          Reference Link
        </label>
        <input
          id="referenceLink"
          type="url"
          value={referenceLink}
          onChange={(e) => setReferenceLink(e.target.value)}
          className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          placeholder="https://example.com/original-recipe"
        />
      </div>

      {/* Submit Button */}
      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 bg-primary text-primary-foreground py-2 px-4 rounded-md hover:opacity-90 hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none transition-all duration-200"
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  );
}
