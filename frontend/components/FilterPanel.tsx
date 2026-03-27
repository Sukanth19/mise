'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronDown, 
  X, 
  Star, 
  Heart,
  Tag,
  Leaf,
  AlertTriangle,
  SortAsc,
  SortDesc,
  Calendar,
  TrendingUp,
  Type
} from 'lucide-react';

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
  'pescatarian',
  'halal',
  'kosher',
];

const ALLERGENS = [
  'nuts',
  'peanuts',
  'dairy',
  'eggs',
  'soy',
  'wheat',
  'fish',
  'shellfish',
  'sesame',
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [favorites, minRating, selectedTags, selectedDietaryLabels, selectedAllergens, sortBy, sortOrder]);

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

  const activeFilterCount = 
    (favorites ? 1 : 0) + 
    (minRating > 1 ? 1 : 0) + 
    selectedTags.length + 
    selectedDietaryLabels.length + 
    selectedAllergens.length;

  const getSortIcon = () => {
    switch (sortBy) {
      case 'date': return Calendar;
      case 'rating': return TrendingUp;
      case 'title': return Type;
      default: return Calendar;
    }
  };

  const SortIcon = getSortIcon();

  return (
    <motion.div 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="comic-panel bg-card p-6 rounded-none mb-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h2 className="text-xl font-black uppercase text-foreground">FILTERS & SORT</h2>
          {activeFilterCount > 0 && (
            <span className="comic-border bg-primary text-primary-foreground px-3 py-1 text-sm font-black">
              {activeFilterCount}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleClearFilters}
              className="comic-button px-4 py-2 bg-destructive text-destructive-foreground text-sm flex items-center gap-2 hover:scale-105 transition-transform"
            >
              <X size={16} strokeWidth={2.5} />
              CLEAR ALL
            </button>
          )}
          <motion.button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="comic-button px-4 py-2 bg-secondary text-secondary-foreground text-sm flex items-center gap-2 hover:scale-105 transition-transform"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            >
              <ChevronDown size={16} strokeWidth={2.5} />
            </motion.div>
            {isExpanded ? 'COLLAPSE' : 'EXPAND'}
          </motion.button>
        </div>
      </div>

      {/* Quick Filters (Always Visible) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Favorites Toggle */}
        <label className="comic-border p-4 cursor-pointer hover:bg-muted/50 transition-colors flex items-center gap-3">
          <input
            type="checkbox"
            checked={favorites === true}
            onChange={(e) => setFavorites(e.target.checked ? true : undefined)}
            className="w-5 h-5 border-4 border-border rounded-none accent-primary"
          />
          <Heart 
            size={20} 
            strokeWidth={2.5} 
            className={favorites ? 'fill-warning text-warning' : 'text-muted-foreground'}
          />
          <span className="font-bold uppercase text-sm">FAVORITES ONLY</span>
        </label>

        {/* Sort Dropdown */}
        <div className="comic-border p-4 flex items-center gap-3">
          <SortIcon size={20} strokeWidth={2.5} className="text-muted-foreground" />
          <select
            id="sort-by-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'rating' | 'title')}
            className="flex-1 bg-transparent text-foreground font-bold uppercase text-sm outline-none cursor-pointer"
            aria-label="Sort recipes by"
          >
            <option value="date">NEWEST FIRST</option>
            <option value="rating">HIGHEST RATED</option>
            <option value="title">ALPHABETICAL</option>
          </select>
          <button
            type="button"
            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            className="comic-border bg-muted text-foreground p-2 hover:bg-muted/80 transition-colors"
            title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
            aria-label={`Sort order: ${sortOrder === 'asc' ? 'Ascending' : 'Descending'}`}
          >
            {sortOrder === 'asc' ? (
              <SortAsc size={18} strokeWidth={2.5} />
            ) : (
              <SortDesc size={18} strokeWidth={2.5} />
            )}
          </button>
        </div>

        {/* Rating Filter */}
        <div className="comic-border p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Star size={20} strokeWidth={2.5} className="text-warning fill-warning" />
              <span className="font-bold uppercase text-sm">MIN RATING</span>
            </div>
            <span className="font-black text-lg">{minRating}★</span>
          </div>
          <input
            id="rating-slider"
            type="range"
            min="1"
            max="5"
            step="1"
            value={minRating}
            onChange={(e) => setMinRating(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-none appearance-none cursor-pointer accent-warning"
            aria-label="Minimum rating filter"
          />
        </div>
      </div>

      {/* Expanded Filters */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ 
              opacity: 1, 
              height: 'auto',
              transition: {
                height: {
                  duration: 0.4,
                  ease: [0.4, 0, 0.2, 1]
                },
                opacity: {
                  duration: 0.3,
                  delay: 0.1
                }
              }
            }}
            exit={{ 
              opacity: 0, 
              height: 0,
              transition: {
                height: {
                  duration: 0.3,
                  ease: [0.4, 0, 0.2, 1]
                },
                opacity: {
                  duration: 0.2
                }
              }
            }}
            className="pt-6 mt-6 border-t-4 border-border overflow-hidden"
          >
            <div className="space-y-6">
              {/* Tags Multi-Select */}
              {availableTags.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ 
                    opacity: 1, 
                    y: 0,
                    transition: {
                      duration: 0.3,
                      delay: 0.1,
                      ease: [0.4, 0, 0.2, 1]
                    }
                  }}
                  exit={{ 
                    opacity: 0, 
                    y: -10,
                    transition: { duration: 0.2 }
                  }}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Tag size={20} strokeWidth={2.5} className="text-muted-foreground" />
                    <label className="font-bold uppercase text-sm">TAGS</label>
                    {selectedTags.length > 0 && (
                      <motion.span 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="text-xs text-muted-foreground"
                      >
                        ({selectedTags.length} selected)
                      </motion.span>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {availableTags.map((tag, index) => (
                      <motion.button
                        key={tag}
                        type="button"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ 
                          opacity: 1, 
                          scale: 1,
                          transition: {
                            duration: 0.2,
                            delay: 0.15 + (index * 0.03),
                            ease: [0.4, 0, 0.2, 1]
                          }
                        }}
                        exit={{ 
                          opacity: 0, 
                          scale: 0.8,
                          transition: { duration: 0.15 }
                        }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleTagToggle(tag)}
                        className={`px-4 py-2 text-sm font-bold uppercase rounded-none transition-colors comic-border ${
                          selectedTags.includes(tag)
                            ? 'bg-primary text-primary-foreground shadow-md'
                            : 'bg-muted text-muted-foreground hover:bg-primary/10'
                        }`}
                      >
                        {tag}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Dietary Labels */}
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ 
                  opacity: 1, 
                  y: 0,
                  transition: {
                    duration: 0.3,
                    delay: availableTags.length > 0 ? 0.2 : 0.1,
                    ease: [0.4, 0, 0.2, 1]
                  }
                }}
                exit={{ 
                  opacity: 0, 
                  y: -10,
                  transition: { duration: 0.2 }
                }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <Leaf size={20} strokeWidth={2.5} className="text-success" />
                  <label className="font-bold uppercase text-sm">DIETARY LABELS</label>
                  {selectedDietaryLabels.length > 0 && (
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="text-xs text-muted-foreground"
                    >
                      ({selectedDietaryLabels.length} selected)
                    </motion.span>
                  )}
                </div>
                <div className="flex flex-wrap gap-2">
                  {DIETARY_LABELS.map((label, index) => (
                    <motion.button
                      key={label}
                      type="button"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ 
                        opacity: 1, 
                        scale: 1,
                        transition: {
                          duration: 0.2,
                          delay: (availableTags.length > 0 ? 0.25 : 0.15) + (index * 0.03),
                          ease: [0.4, 0, 0.2, 1]
                        }
                      }}
                      exit={{ 
                        opacity: 0, 
                        scale: 0.8,
                        transition: { duration: 0.15 }
                      }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleDietaryLabelToggle(label)}
                      className={`px-4 py-2 text-sm font-bold uppercase rounded-none transition-colors comic-border ${
                        selectedDietaryLabels.includes(label)
                          ? 'bg-success text-success-foreground shadow-md'
                          : 'bg-muted text-muted-foreground hover:bg-success/10'
                      }`}
                    >
                      {label}
                    </motion.button>
                  ))}
                </div>
              </motion.div>

              {/* Allergen Exclusion */}
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ 
                  opacity: 1, 
                  y: 0,
                  transition: {
                    duration: 0.3,
                    delay: availableTags.length > 0 ? 0.3 : 0.2,
                    ease: [0.4, 0, 0.2, 1]
                  }
                }}
                exit={{ 
                  opacity: 0, 
                  y: -10,
                  transition: { duration: 0.2 }
                }}
              >
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle size={20} strokeWidth={2.5} className="text-destructive" />
                  <label className="font-bold uppercase text-sm">EXCLUDE ALLERGENS</label>
                  {selectedAllergens.length > 0 && (
                    <motion.span 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="text-xs text-muted-foreground"
                    >
                      ({selectedAllergens.length} excluded)
                    </motion.span>
                  )}
                </div>
                <div className="flex flex-wrap gap-2">
                  {ALLERGENS.map((allergen, index) => (
                    <motion.button
                      key={allergen}
                      type="button"
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ 
                        opacity: 1, 
                        scale: 1,
                        transition: {
                          duration: 0.2,
                          delay: (availableTags.length > 0 ? 0.35 : 0.25) + (index * 0.03),
                          ease: [0.4, 0, 0.2, 1]
                        }
                      }}
                      exit={{ 
                        opacity: 0, 
                        scale: 0.8,
                        transition: { duration: 0.15 }
                      }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleAllergenToggle(allergen)}
                      className={`px-4 py-2 text-sm font-bold uppercase rounded-none transition-colors comic-border ${
                        selectedAllergens.includes(allergen)
                          ? 'bg-destructive text-destructive-foreground shadow-md'
                          : 'bg-muted text-muted-foreground hover:bg-destructive/10'
                      }`}
                    >
                      {allergen}
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
