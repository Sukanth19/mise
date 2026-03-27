'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { Recipe, Collection } from '@/types';
import RecipeGrid from '@/components/RecipeGrid';
import SearchBar from '@/components/SearchBar';
import FilterPanel, { FilterOptions } from '@/components/FilterPanel';
import AddToCollectionModal from '@/components/AddToCollectionModal';
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal';
import LoadingSpinner from '@/components/LoadingSpinner';
import { Trash2, FolderPlus, X } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({});
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  
  // Bulk operations state
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedRecipeIds, setSelectedRecipeIds] = useState<Set<number>>(new Set());
  const [collections, setCollections] = useState<Collection[]>([]);
  const [showAddToCollectionModal, setShowAddToCollectionModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchRecipes();
    fetchCollections();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchRecipes = async (search?: string, filterOptions?: FilterOptions) => {
    try {
      setLoading(true);
      setError(null);
      
      // Build query parameters
      const params = new URLSearchParams();
      
      // Add search if provided
      if (search) {
        params.append('search', search);
      }
      
      // Add filter parameters if provided
      if (filterOptions && typeof filterOptions === 'object') {
        if (filterOptions.favorites !== undefined) {
          params.append('favorites', String(filterOptions.favorites));
        }
        if (filterOptions.minRating !== undefined) {
          params.append('min_rating', String(filterOptions.minRating));
        }
        if (Array.isArray(filterOptions.tags) && filterOptions.tags.length > 0) {
          params.append('tags', filterOptions.tags.join(','));
        }
        if (Array.isArray(filterOptions.dietaryLabels) && filterOptions.dietaryLabels.length > 0) {
          params.append('dietary_labels', filterOptions.dietaryLabels.join(','));
        }
        if (Array.isArray(filterOptions.excludeAllergens) && filterOptions.excludeAllergens.length > 0) {
          params.append('exclude_allergens', filterOptions.excludeAllergens.join(','));
        }
        if (filterOptions.sortBy) {
          params.append('sort_by', filterOptions.sortBy);
        }
        if (filterOptions.sortOrder) {
          params.append('sort_order', filterOptions.sortOrder);
        }
      }
      
      // Determine endpoint based on whether filters are applied
      const hasFilters = filterOptions && Object.keys(filterOptions).some(key => {
        const value = filterOptions[key as keyof FilterOptions];
        return value !== undefined && (Array.isArray(value) ? value.length > 0 : true);
      });
      
      const endpoint = hasFilters 
        ? `/api/recipes/filter?${params.toString()}`
        : search 
          ? `/api/recipes?search=${encodeURIComponent(search)}`
          : '/api/recipes';
      
      // Fetch data
      const data = await apiClient<Recipe[]>(endpoint);
      
      setRecipes(data);
      setFilteredRecipes(data);
      
      // Extract unique tags from all recipes for the filter panel
      const tags = new Set<string>();
      data.forEach(recipe => {
        if (recipe.tags) {
          recipe.tags.forEach(tag => tags.add(tag));
        }
      });
      setAvailableTags(Array.from(tags).sort());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recipes');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = useCallback((query: string) => {
    console.log('SEARCH CLICKED:', query);
    setSearchQuery(query);
    fetchRecipes(query.trim() === '' ? undefined : query, filters);
  }, [filters, fetchRecipes]);

  const handleFilterChange = useCallback((newFilters: FilterOptions) => {
    setFilters(newFilters);
    fetchRecipes(searchQuery.trim() === '' ? undefined : searchQuery, newFilters);
  }, [searchQuery, fetchRecipes]);

  const handleCreateRecipe = useCallback(() => {
    console.log('CREATE RECIPE CLICKED');
    window.location.href = '/recipes/new';
  }, []);

  const fetchCollections = async () => {
    try {
      const data = await apiClient<{ collections: Collection[] }>('/api/collections');
      setCollections(data.collections);
    } catch (err) {
      console.error('Failed to fetch collections:', err);
    }
  };

  const handleToggleSelection = (recipeId: number) => {
    setSelectedRecipeIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(recipeId)) {
        newSet.delete(recipeId);
      } else {
        newSet.add(recipeId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedRecipeIds.size === filteredRecipes.length) {
      setSelectedRecipeIds(new Set());
    } else {
      setSelectedRecipeIds(new Set(filteredRecipes.map(r => r.id)));
    }
  };

  const handleBulkDelete = async () => {
    try {
      setIsDeleting(true);
      await apiClient('/api/recipes/bulk', {
        method: 'DELETE',
        body: JSON.stringify({ recipe_ids: Array.from(selectedRecipeIds) }),
      });
      setShowDeleteModal(false);
      setSelectedRecipeIds(new Set());
      setSelectionMode(false);
      await fetchRecipes();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete recipes');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleBulkAddToCollections = async (collectionIds: number[]) => {
    try {
      // Add selected recipes to each collection
      await Promise.all(
        collectionIds.map(collectionId =>
          apiClient(`/api/collections/${collectionId}/recipes`, {
            method: 'POST',
            body: JSON.stringify({ recipe_ids: Array.from(selectedRecipeIds) }),
          })
        )
      );
      setShowAddToCollectionModal(false);
      setSelectedRecipeIds(new Set());
      setSelectionMode(false);
      alert('Recipes added to collections successfully!');
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to add to collections');
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8 flex items-center justify-center">
        <LoadingSpinner variant="recipe" size="lg" text="Loading recipes..." />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <h1 className="text-4xl comic-heading text-foreground mb-4 md:mb-0">MY RECIPES</h1>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => {
                setSelectionMode(!selectionMode);
                setSelectedRecipeIds(new Set());
              }}
              className={`comic-button px-6 py-4 rounded-none ${
                selectionMode 
                  ? 'bg-secondary text-secondary-foreground' 
                  : 'bg-muted text-muted-foreground'
              }`}
            >
              {selectionMode ? 'CANCEL SELECT' : 'SELECT RECIPES'}
            </button>
            <button
              type="button"
              onClick={handleCreateRecipe}
              className="comic-button px-8 py-4 bg-primary text-primary-foreground rounded-none"
            >
              CREATE RECIPE
            </button>
          </div>
        </div>

        {/* Bulk Actions Toolbar */}
        {selectionMode && selectedRecipeIds.size > 0 && (
          <div className="mb-6 comic-panel p-4 bg-secondary/10 border-secondary flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="font-black text-foreground uppercase">
                {selectedRecipeIds.size} RECIPE{selectedRecipeIds.size !== 1 ? 'S' : ''} SELECTED
              </span>
              <button
                type="button"
                onClick={handleSelectAll}
                className="text-sm font-bold text-secondary hover:underline uppercase"
              >
                {selectedRecipeIds.size === filteredRecipes.length ? 'DESELECT ALL' : 'SELECT ALL'}
              </button>
            </div>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setShowAddToCollectionModal(true)}
                className="comic-button px-4 py-2 bg-secondary text-secondary-foreground flex items-center gap-2"
              >
                <FolderPlus size={18} strokeWidth={2.5} />
                ADD TO COLLECTION
              </button>
              <button
                type="button"
                onClick={() => setShowDeleteModal(true)}
                className="comic-button px-4 py-2 bg-destructive text-destructive-foreground flex items-center gap-2"
              >
                <Trash2 size={18} strokeWidth={2.5} />
                DELETE
              </button>
            </div>
          </div>
        )}

        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} value={searchQuery} />
        </div>

        {/* Filter Panel */}
        <FilterPanel onFilterChange={handleFilterChange} availableTags={availableTags} />

        {/* Error Message */}
        {error && (
          <div className="mb-6 comic-panel bg-destructive text-destructive-foreground p-4 rounded-none font-bold">
            {error}
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredRecipes && filteredRecipes.length === 0 && !searchQuery && (
          <div className="text-center py-12">
            <div className="mb-6">
              <svg
                className="mx-auto h-32 w-32 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={3}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <h2 className="text-2xl font-black text-foreground mb-3 uppercase">No recipes yet</h2>
            <p className="text-muted-foreground mb-8 font-bold uppercase">Start building your recipe collection!</p>
            <button
              type="button"
              onClick={handleCreateRecipe}
              className="comic-button px-8 py-4 bg-primary text-primary-foreground rounded-none"
            >
              CREATE YOUR FIRST RECIPE
            </button>
          </div>
        )}

        {/* Search Results Empty State */}
        {!loading && filteredRecipes && filteredRecipes.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <p className="text-muted-foreground font-bold uppercase">No recipes found matching "{searchQuery}"</p>
          </div>
        )}

        {/* Recipe Grid */}
        {!loading && filteredRecipes && filteredRecipes.length > 0 && (
          <RecipeGrid 
            recipes={filteredRecipes}
            selectionMode={selectionMode}
            selectedRecipeIds={selectedRecipeIds}
            onToggleSelection={handleToggleSelection}
          />
        )}

        {/* Add to Collection Modal */}
        <AddToCollectionModal
          isOpen={showAddToCollectionModal}
          onClose={() => setShowAddToCollectionModal(false)}
          onSubmit={handleBulkAddToCollections}
          collections={collections}
        />

        {/* Delete Confirmation Modal */}
        <DeleteConfirmationModal
          isOpen={showDeleteModal}
          onClose={() => setShowDeleteModal(false)}
          onConfirm={handleBulkDelete}
          title={`${selectedRecipeIds.size} recipe${selectedRecipeIds.size !== 1 ? 's' : ''}`}
          isDeleting={isDeleting}
        />
      </div>
    </main>
  );
}
