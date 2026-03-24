'use client';

import { useState, FormEvent } from 'react';

export interface NutritionData {
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
  servings?: number;
}

interface NutritionFormProps {
  initialData?: NutritionData;
  onSubmit: (data: NutritionData) => Promise<void>;
  onCancel?: () => void;
}

export default function NutritionForm({ 
  initialData, 
  onSubmit,
  onCancel 
}: NutritionFormProps) {
  const [calories, setCalories] = useState<string>(initialData?.calories?.toString() || '');
  const [proteinG, setProteinG] = useState<string>(initialData?.protein_g?.toString() || '');
  const [carbsG, setCarbsG] = useState<string>(initialData?.carbs_g?.toString() || '');
  const [fatG, setFatG] = useState<string>(initialData?.fat_g?.toString() || '');
  const [fiberG, setFiberG] = useState<string>(initialData?.fiber_g?.toString() || '');
  const [servings, setServings] = useState<string>(initialData?.servings?.toString() || '1');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateNonNegative = (value: string, fieldName: string): boolean => {
    if (value === '') return true; // Empty is allowed (optional field)
    const num = parseFloat(value);
    if (isNaN(num)) {
      setError(`${fieldName} must be a valid number`);
      return false;
    }
    if (num < 0) {
      setError(`${fieldName} cannot be negative`);
      return false;
    }
    return true;
  };

  const validateForm = (): boolean => {
    setError(null);

    if (!validateNonNegative(calories, 'Calories')) return false;
    if (!validateNonNegative(proteinG, 'Protein')) return false;
    if (!validateNonNegative(carbsG, 'Carbs')) return false;
    if (!validateNonNegative(fatG, 'Fat')) return false;
    if (!validateNonNegative(fiberG, 'Fiber')) return false;

    // Validate servings (required and must be positive)
    const servingsNum = parseFloat(servings);
    if (isNaN(servingsNum) || servingsNum <= 0) {
      setError('Serving size must be a positive number');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const nutritionData: NutritionData = {
        calories: calories ? parseFloat(calories) : undefined,
        protein_g: proteinG ? parseFloat(proteinG) : undefined,
        carbs_g: carbsG ? parseFloat(carbsG) : undefined,
        fat_g: fatG ? parseFloat(fatG) : undefined,
        fiber_g: fiberG ? parseFloat(fiberG) : undefined,
        servings: servings ? parseFloat(servings) : 1,
      };

      await onSubmit(nutritionData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save nutrition facts');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="comic-border bg-destructive/10 border-destructive text-destructive px-4 py-3 font-bold" role="alert">
          ⚠️ {error}
        </div>
      )}

      {/* Serving Size */}
      <div>
        <label htmlFor="servings" className="block font-bold uppercase text-sm mb-2">
          Serving Size <span className="text-destructive">*</span>
        </label>
        <input
          id="servings"
          type="number"
          step="0.1"
          value={servings}
          onChange={(e) => setServings(e.target.value)}
          className="w-full comic-input px-4 py-2 font-medium"
          placeholder="Number of servings"
          required
        />
        <p className="mt-1 text-xs text-muted-foreground font-medium">
          Total servings this recipe makes
        </p>
      </div>

      {/* Nutrition Facts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Calories */}
        <div>
          <label htmlFor="calories" className="block font-bold uppercase text-sm mb-2">
            Calories
          </label>
          <input
            id="calories"
            type="number"
            step="0.1"
            value={calories}
            onChange={(e) => setCalories(e.target.value)}
            className="w-full comic-input px-4 py-2 font-medium"
            placeholder="0"
          />
        </div>

        {/* Protein */}
        <div>
          <label htmlFor="protein" className="block font-bold uppercase text-sm mb-2">
            Protein (g)
          </label>
          <input
            id="protein"
            type="number"
            step="0.1"
            value={proteinG}
            onChange={(e) => setProteinG(e.target.value)}
            className="w-full comic-input px-4 py-2 font-medium"
            placeholder="0"
          />
        </div>

        {/* Carbs */}
        <div>
          <label htmlFor="carbs" className="block font-bold uppercase text-sm mb-2">
            Carbs (g)
          </label>
          <input
            id="carbs"
            type="number"
            step="0.1"
            value={carbsG}
            onChange={(e) => setCarbsG(e.target.value)}
            className="w-full comic-input px-4 py-2 font-medium"
            placeholder="0"
          />
        </div>

        {/* Fat */}
        <div>
          <label htmlFor="fat" className="block font-bold uppercase text-sm mb-2">
            Fat (g)
          </label>
          <input
            id="fat"
            type="number"
            step="0.1"
            value={fatG}
            onChange={(e) => setFatG(e.target.value)}
            className="w-full comic-input px-4 py-2 font-medium"
            placeholder="0"
          />
        </div>

        {/* Fiber */}
        <div>
          <label htmlFor="fiber" className="block font-bold uppercase text-sm mb-2">
            Fiber (g)
          </label>
          <input
            id="fiber"
            type="number"
            step="0.1"
            value={fiberG}
            onChange={(e) => setFiberG(e.target.value)}
            className="w-full comic-input px-4 py-2 font-medium"
            placeholder="0"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 pt-4">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="comic-button px-6 py-3 bg-muted text-foreground font-bold disabled:opacity-50"
          >
            CANCEL
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 comic-button bg-primary text-primary-foreground py-3 px-6 font-bold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'SAVING...' : 'SAVE NUTRITION FACTS'}
        </button>
      </div>
    </form>
  );
}
