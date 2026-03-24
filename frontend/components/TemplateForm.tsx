'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Trash2, X } from 'lucide-react';
import { Recipe, TemplateCreate } from '@/types';
import { apiClient } from '@/lib/api';

type MealTime = 'breakfast' | 'lunch' | 'dinner' | 'snack';

interface TemplateFormProps {
  onSubmit: (template: TemplateCreate) => void;
  onCancel: () => void;
}

interface TemplateItem {
  recipe_id: number;
  recipe?: Recipe;
  day_offset: number;
  meal_time: MealTime;
}

export default function TemplateForm({ onSubmit, onCancel }: TemplateFormProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [items, setItems] = useState<TemplateItem[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch user's recipes
  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        const data = await apiClient<{ recipes: Recipe[] }>('/api/recipes');
        setRecipes(data.recipes);
      } catch (err) {
        setError('Failed to load recipes');
      } finally {
        setLoading(false);
      }
    };
    fetchRecipes();
  }, []);

  const addItem = () => {
    if (recipes.length === 0) {
      setError('No recipes available. Create some recipes first.');
      return;
    }
    setItems([
      ...items,
      {
        recipe_id: recipes[0].id,
        recipe: recipes[0],
        day_offset: 0,
        meal_time: 'breakfast',
      },
    ]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: keyof TemplateItem, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    
    // If recipe_id changed, update the recipe object
    if (field === 'recipe_id') {
      const recipe = recipes.find((r) => r.id === value);
      newItems[index].recipe = recipe;
    }
    
    setItems(newItems);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Template name is required');
      return;
    }

    if (items.length === 0) {
      setError('Add at least one recipe to the template');
      return;
    }

    const template: TemplateCreate = {
      name: name.trim(),
      description: description.trim() || undefined,
      items: items.map((item) => ({
        recipe_id: item.recipe_id,
        day_offset: item.day_offset,
        meal_time: item.meal_time,
      })),
    };

    onSubmit(template);
  };

  if (loading) {
    return (
      <div className="comic-panel rounded-none p-6 bg-card">
        <p className="text-center text-muted-foreground">Loading recipes...</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="comic-panel rounded-none p-6 bg-card"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-black uppercase tracking-wide">
          Create Meal Plan Template
        </h2>
        <button
          type="button"
          onClick={onCancel}
          className="comic-button p-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
          aria-label="Close"
        >
          <X size={20} />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Template name */}
        <div>
          <label htmlFor="template-name" className="block font-bold text-sm uppercase mb-2">
            Template Name *
          </label>
          <input
            id="template-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full comic-input"
            placeholder="e.g., Weekly Meal Plan"
            required
          />
        </div>

        {/* Template description */}
        <div>
          <label htmlFor="template-description" className="block font-bold text-sm uppercase mb-2">
            Description (Optional)
          </label>
          <textarea
            id="template-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full comic-input min-h-[80px]"
            placeholder="Describe this meal plan template..."
          />
        </div>

        {/* Template items */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block font-bold text-sm uppercase">
              Recipes
            </label>
            <button
              type="button"
              onClick={addItem}
              className="comic-button px-3 py-1 bg-primary text-primary-foreground hover:bg-primary/80 flex items-center gap-1"
            >
              <Plus size={16} />
              ADD RECIPE
            </button>
          </div>

          {items.length === 0 ? (
            <div className="comic-border p-6 text-center text-muted-foreground">
              <p className="font-medium">No recipes added yet</p>
              <p className="text-sm mt-1">Click "Add Recipe" to start building your template</p>
            </div>
          ) : (
            <div className="space-y-3">
              {items.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="comic-border p-4 bg-background"
                >
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    {/* Recipe selection */}
                    <div className="md:col-span-2">
                      <label htmlFor={`recipe-${index}`} className="block font-bold text-xs uppercase mb-1">
                        Recipe
                      </label>
                      <select
                        id={`recipe-${index}`}
                        value={item.recipe_id}
                        onChange={(e) => updateItem(index, 'recipe_id', parseInt(e.target.value))}
                        className="w-full comic-input text-sm"
                      >
                        {recipes.map((recipe) => (
                          <option key={recipe.id} value={recipe.id}>
                            {recipe.title}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Day offset */}
                    <div>
                      <label htmlFor={`day-${index}`} className="block font-bold text-xs uppercase mb-1">
                        Day
                      </label>
                      <input
                        id={`day-${index}`}
                        type="number"
                        min="0"
                        max="30"
                        value={item.day_offset}
                        onChange={(e) => updateItem(index, 'day_offset', parseInt(e.target.value))}
                        className="w-full comic-input text-sm"
                      />
                    </div>

                    {/* Meal time */}
                    <div>
                      <label htmlFor={`meal-time-${index}`} className="block font-bold text-xs uppercase mb-1">
                        Meal Time
                      </label>
                      <div className="flex items-center gap-2">
                        <select
                          id={`meal-time-${index}`}
                          value={item.meal_time}
                          onChange={(e) => updateItem(index, 'meal_time', e.target.value as MealTime)}
                          className="flex-1 comic-input text-sm"
                        >
                          <option value="breakfast">Breakfast</option>
                          <option value="lunch">Lunch</option>
                          <option value="dinner">Dinner</option>
                          <option value="snack">Snack</option>
                        </select>
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="comic-button p-2 bg-destructive text-destructive-foreground hover:bg-destructive/80"
                          aria-label="Remove recipe"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Error message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="comic-border p-3 bg-destructive/10 text-destructive font-bold text-sm"
          >
            {error}
          </motion.div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3 justify-end">
          <button
            type="button"
            onClick={onCancel}
            className="comic-button px-6 py-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
          >
            CANCEL
          </button>
          <button
            type="submit"
            className="comic-button px-6 py-2 bg-primary text-primary-foreground hover:bg-primary/80"
          >
            CREATE TEMPLATE
          </button>
        </div>
      </form>
    </motion.div>
  );
}
