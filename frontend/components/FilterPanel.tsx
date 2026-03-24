'use client';

import { useState, useEffect } from 'react';

export interface FilterOptions {
  favorites?: boolean;
  minRating?: number;
  tags?: string[];
  dietaryLabels?: string[];
  excludeAllergens?: string[];
  sortBy?: 'date' | 'rating' | 'title';
  sortOrder?: 'asc' | 'desc';
}

interface FilterPanelProps {
  onFilterChange: (filters: FilterOptions) => void;
  availableTags?: string[];
}

const DIETARY_LABELS = [
  'vegan',
  'vegetarian',
  'gluten-free',
  'dairy-free',
  'keto',
  'paleo',
  'low-carb',
];

const ALLERGENS = [
  'nuts',
  'dairy',
  'eggs',
  'soy',
  'wheat',
  'fish',
  'shellfish',
];

export default function FilterPanel({ onFilterChange, availableTags = [] }: FilterPanelProps) {
  const [favorites, setFavorites] = useState<boolean | undefined>(undefined);
  const [minRating, setMinRating] = useState<number>(1);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedDietaryLabels, setSelectedDietaryLabels] = useState<string[]>([]);
  const [selectedAllergens, setSelectedAllergens] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<'date' | 'rating' | 'title'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const filters: FilterOptions = {
      favorites: favorites,
      minRating: minRating > 1 ? minRating : undefined,
      tags: selectedTags.length > 0 ? selectedTags : undefined,
      dietaryLabels: selectedDietaryLabels.length > 0 ? selectedDietaryLabels : undefined,
      excludeAllergens: selectedAllergens.length > 0 ? selectedAllergens : undefined,
      sortBy,
      sortOrder,
    };
    onFilterChange(filters);
  }, [favorites, minRating, selectedTags, selectedDietaryLabels, selectedAllergens, sortBy, sortOrder, onFilterChange]);

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  const handleDietaryLabelToggle = (label: string) => {
    setSelectedDietaryLabels(prev =>
      prev.includes(label) ? prev.filter(l => l !== label) : [...prev, label]
    );
  };

  const handleAllergenToggle = (allergen: string) => {
    setSelectedAllergens(prev =>
      prev.includes(allergen) ? prev.filter(a => a !== allergen) : [...prev, allergen]
    );
  };

  const handleClearFilters = () => {
    setFavorites(undefined);
    setMinRating(1);
    setSelectedTags([]);
    setSelectedDietaryLabels([]);
    setSelectedAllergens([]);
    setSortBy('date');
    setSortOrder('desc');
  };

  const hasActiveFilters = favorites !== undefined || minRating > 1 || selectedTags.length > 0 || 
    selectedDietaryLabels.length > 0 || selectedAllergens.length > 0;

  return (
    <div className="comic-panel bg-card p-6 rounded-none mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-black uppercase text-foreground">FILTERS & SORT</h2>
        <div className="flex gap-2">
          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleClearFilters}
              className="text-sm font-bold uppercase text-muted-foreground hover:text-foreground transition-colors"
            >
              CLEAR ALL
            </button>
          )}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm font-bold uppercase text-primary hover:text-primary/80 transition-colors"
          >
            {isExpanded ? 'COLLAPSE' : 'EXPAND'}
          </button>
        </div>
      </div>

      {/* Quick Filters (Always Visible) */}
      <div className="flex flex-wrap gap-4 mb-4">
        {/* Favorites Toggle */}
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={favorites === true}
            onChange={(e) => setFavorites(e.target.checked ? true : undefined)}
            className="w-5 h-5 border-4 border-border rounded-none accent-primary"
          />
          <span className="font-bold uppercase text-sm">FAVORITES ONLY</span>
        </label>

        {/* Sort Dropdown */}
        <div className="flex items-center gap-2">
          <label htmlFor="sort-by-select" className="font-bold uppercase text-sm">SORT BY:</label>
          <select
            id="sort-by-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'rating' | 'title')}
            className="comic-border bg-input text-foreground px-3 py-1 font-bold uppercase text-sm"
          >
            <option value="date">DATE</option>
            <option value="rating">RATING</option>
            <option value="title">TITLE</option>
          </select>
          <button
            type="button"
            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            className="comic-border bg-input text-foreground px-3 py-1 font-bold uppercase text-sm hover:bg-muted transition-colors"
            title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
            aria-label={`Sort order: ${sortOrder === 'asc' ? 'Ascending' : 'Descending'}`}
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="space-y-6 pt-4 border-t-4 border-border">
          {/* Rating Slider */}
          <div>
            <label htmlFor="rating-slider" className="block font-bold uppercase text-sm mb-2">
              MIN RATING: {minRating} {minRating > 1 ? '★' : '(ALL)'}
            </label>
            <input
              id="rating-slider"
              type="range"
              min="1"
              max="5"
              step="1"
              value={minRating}
              onChange={(e) => setMinRating(Number(e.target.value))}
              className="w-full h-2 bg-muted rounded-none appearance-none cursor-pointer accent-primary"
              aria-label="Minimum rating filter"
            />
            <div className="flex justify-between text-xs font-bold text-muted-foreground mt-1">
              <span>1★</span>
              <span>2★</span>
              <span>3★</span>
              <span>4★</span>
              <span>5★</span>
            </div>
          </div>

          {/* Tags Multi-Select */}
          {availableTags.length > 0 && (
            <div>
              <label className="block font-bold uppercase text-sm mb-2">TAGS</label>
              <div className="flex flex-wrap gap-2">
                {availableTags.map(tag => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => handleTagToggle(tag)}
                    className={`px-3 py-1 text-sm font-bold uppercase rounded-none transition-colors ${
                      selectedTags.includes(tag)
                        ? 'bg-primary text-primary-foreground comic-border'
                        : 'bg-muted text-muted-foreground border-2 border-border hover:bg-muted/80'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Dietary Labels */}
          <div>
            <label className="block font-bold uppercase text-sm mb-2">DIETARY LABELS</label>
            <div className="flex flex-wrap gap-2">
              {DIETARY_LABELS.map(label => (
                <button
                  key={label}
                  type="button"
                  onClick={() => handleDietaryLabelToggle(label)}
                  className={`px-3 py-1 text-sm font-bold uppercase rounded-none transition-colors ${
                    selectedDietaryLabels.includes(label)
                      ? 'bg-secondary text-secondary-foreground comic-border'
                      : 'bg-muted text-muted-foreground border-2 border-border hover:bg-muted/80'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Allergen Exclusion */}
          <div>
            <label className="block font-bold uppercase text-sm mb-2">EXCLUDE ALLERGENS</label>
            <div className="flex flex-wrap gap-2">
              {ALLERGENS.map(allergen => (
                <button
                  key={allergen}
                  type="button"
                  onClick={() => handleAllergenToggle(allergen)}
                  className={`px-3 py-1 text-sm font-bold uppercase rounded-none transition-colors ${
                    selectedAllergens.includes(allergen)
                      ? 'bg-destructive text-destructive-foreground comic-border'
                      : 'bg-muted text-muted-foreground border-2 border-border hover:bg-muted/80'
                  }`}
                >
                  {allergen}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
