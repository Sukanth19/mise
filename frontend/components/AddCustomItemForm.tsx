'use client';

import { useState } from 'react';
import { CustomItemCreate } from '@/types';
import { Plus } from 'lucide-react';

interface AddCustomItemFormProps {
  onAdd: (item: CustomItemCreate) => void;
}

export default function AddCustomItemForm({ onAdd }: AddCustomItemFormProps) {
  const [ingredientName, setIngredientName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [category, setCategory] = useState<'produce' | 'dairy' | 'meat' | 'pantry' | 'other'>('other');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!ingredientName.trim()) {
      return;
    }

    onAdd({
      ingredient_name: ingredientName.trim(),
      quantity: quantity.trim() || undefined,
      category,
    });

    // Reset form
    setIngredientName('');
    setQuantity('');
    setCategory('other');
  };

  return (
    <form onSubmit={handleSubmit} className="comic-panel p-4 bg-card">
      <h3 className="text-lg font-black text-foreground uppercase tracking-wide mb-4">
        Add Custom Item
      </h3>
      
      <div className="space-y-4">
        <div>
          <label htmlFor="ingredient-name" className="block text-sm font-bold text-foreground mb-2">
            ITEM NAME *
          </label>
          <input
            id="ingredient-name"
            type="text"
            value={ingredientName}
            onChange={(e) => setIngredientName(e.target.value)}
            placeholder="e.g., Paper towels"
            className="w-full p-3 border-4 border-border bg-background text-foreground font-medium focus:outline-none focus:border-primary"
            required
            data-testid="ingredient-name-input"
          />
        </div>

        <div>
          <label htmlFor="quantity" className="block text-sm font-bold text-foreground mb-2">
            QUANTITY
          </label>
          <input
            id="quantity"
            type="text"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="e.g., 2 rolls"
            className="w-full p-3 border-4 border-border bg-background text-foreground font-medium focus:outline-none focus:border-primary"
            data-testid="quantity-input"
          />
        </div>

        <div>
          <label htmlFor="category" className="block text-sm font-bold text-foreground mb-2">
            CATEGORY
          </label>
          <select
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value as any)}
            className="w-full p-3 border-4 border-border bg-background text-foreground font-medium focus:outline-none focus:border-primary"
            data-testid="category-select"
          >
            <option value="produce">Produce</option>
            <option value="dairy">Dairy</option>
            <option value="meat">Meat & Seafood</option>
            <option value="pantry">Pantry</option>
            <option value="other">Other</option>
          </select>
        </div>

        <button
          type="submit"
          className="comic-button w-full p-3 bg-primary text-primary-foreground hover:bg-primary/80 flex items-center justify-center gap-2"
          data-testid="add-button"
        >
          <Plus size={20} strokeWidth={3} />
          <span className="font-bold">ADD ITEM</span>
        </button>
      </div>
    </form>
  );
}
