'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { MealPlan, Recipe, MealPlanTemplate, TemplateCreate, NutritionSummaryResponse } from '@/types';
import MealPlannerCalendar from '@/components/MealPlannerCalendar';
import TemplateForm from '@/components/TemplateForm';
import TemplateList from '@/components/TemplateList';
import EmptyState from '@/components/EmptyState';
import NutritionSummary from '@/components/NutritionSummary';
import { Calendar, Download, Plus, Search, X, FileText, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

type MealTime = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export default function MealPlannerPage() {
  const router = useRouter();
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [templates, setTemplates] = useState<MealPlanTemplate[]>([]);
  const [nutritionSummary, setNutritionSummary] = useState<NutritionSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [showSidebar, setShowSidebar] = useState(true);
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [showTemplateList, setShowTemplateList] = useState(false);
  const [showNutritionSummary, setShowNutritionSummary] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [draggedRecipe, setDraggedRecipe] = useState<Recipe | null>(null);
  
  // Date range for fetching meal plans (current week by default)
  const [dateRange, setDateRange] = useState(() => {
    const today = new Date();
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - today.getDay()); // Sunday
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6); // Saturday
    return {
      start: weekStart.toISOString().split('T')[0],
      end: weekEnd.toISOString().split('T')[0],
    };
  });

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dateRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch meal plans, recipes, templates, and nutrition summary in parallel
      const [mealPlansData, recipesData, templatesData, nutritionData] = await Promise.all([
        apiClient<{ meal_plans: MealPlan[] }>(
          `/api/meal-plans?start_date=${dateRange.start}&end_date=${dateRange.end}`
        ),
        apiClient<{ recipes: Recipe[] }>('/api/recipes'),
        apiClient<{ templates: MealPlanTemplate[] }>('/api/meal-plan-templates'),
        apiClient<NutritionSummaryResponse>(
          `/api/meal-plans/nutrition-summary?start_date=${dateRange.start}&end_date=${dateRange.end}`
        ).catch(() => null), // Nutrition summary is optional
      ]);
      
      setMealPlans(mealPlansData.meal_plans || []);
      setRecipes(recipesData.recipes || []);
      setTemplates(templatesData.templates || []);
      setNutritionSummary(nutritionData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setMealPlans([]);
      setRecipes([]);
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle recipe drop onto calendar
  const handleRecipeDrop = async (recipeId: number, date: string, mealTime: MealTime) => {
    try {
      const newMealPlan = await apiClient<MealPlan>('/api/meal-plans', {
        method: 'POST',
        body: JSON.stringify({
          recipe_id: recipeId,
          meal_date: date,
          meal_time: mealTime,
        }),
      });
      
      setMealPlans([...mealPlans, newMealPlan]);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add meal plan');
    }
  };

  // Handle meal plan update (drag between dates)
  const handleMealPlanUpdate = async (mealPlanId: number, date: string, mealTime: MealTime) => {
    try {
      const updatedMealPlan = await apiClient<MealPlan>(`/api/meal-plans/${mealPlanId}`, {
        method: 'PUT',
        body: JSON.stringify({
          meal_date: date,
          meal_time: mealTime,
        }),
      });
      
      setMealPlans(mealPlans.map(mp => mp.id === mealPlanId ? updatedMealPlan : mp));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update meal plan');
    }
  };

  // Handle meal plan deletion
  const handleMealPlanDelete = async (mealPlanId: number) => {
    try {
      await apiClient(`/api/meal-plans/${mealPlanId}`, {
        method: 'DELETE',
      });
      
      setMealPlans(mealPlans.filter(mp => mp.id !== mealPlanId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete meal plan');
    }
  };

  // Handle iCal export
  const handleExportICal = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/meal-plans/export?start_date=${dateRange.start}&end_date=${dateRange.end}`,
        {
          headers: {
            Authorization: `Bearer ${getToken()}`,
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to export meal plan');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `meal-plan-${dateRange.start}-to-${dateRange.end}.ics`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to export meal plan');
    }
  };

  // Handle template creation
  const handleCreateTemplate = async (template: TemplateCreate) => {
    try {
      const newTemplate = await apiClient<MealPlanTemplate>('/api/meal-plan-templates', {
        method: 'POST',
        body: JSON.stringify(template),
      });
      
      setTemplates([...templates, newTemplate]);
      setShowTemplateForm(false);
      alert('Template created successfully!');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create template');
    }
  };

  // Handle template application
  const handleApplyTemplate = async (templateId: number) => {
    const startDate = prompt('Enter start date (YYYY-MM-DD):');
    if (!startDate) return;
    
    try {
      const result = await apiClient<{ created_count: number }>(
        `/api/meal-plan-templates/${templateId}/apply`,
        {
          method: 'POST',
          body: JSON.stringify({ start_date: startDate }),
        }
      );
      
      alert(`Created ${result.created_count} meal plans from template!`);
      await fetchData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to apply template');
    }
  };

  // Handle template deletion
  const handleDeleteTemplate = async (templateId: number) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    try {
      await apiClient(`/api/meal-plan-templates/${templateId}`, {
        method: 'DELETE',
      });
      
      setTemplates(templates.filter(t => t.id !== templateId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete template');
    }
  };

  // Filter recipes based on search query
  const filteredRecipes = (recipes || []).filter(recipe =>
    recipe.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle recipe drag start
  const handleDragStart = (e: React.DragEvent, recipe: Recipe) => {
    setDraggedRecipe(recipe);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('application/json', JSON.stringify({
      type: 'recipe',
      recipeId: recipe.id,
    }));
  };

  // Handle recipe drag end
  const handleDragEnd = () => {
    setDraggedRecipe(null);
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <p className="text-muted-foreground font-black text-2xl uppercase">Loading meal planner...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <h1 className="text-4xl comic-heading text-foreground mb-4 md:mb-0">MEAL PLANNER</h1>
          <div className="flex gap-3 flex-wrap">
            <button
              type="button"
              onClick={() => setShowSidebar(!showSidebar)}
              className="comic-button px-4 py-2 bg-secondary text-secondary-foreground"
            >
              {showSidebar ? 'HIDE' : 'SHOW'} RECIPES
            </button>
            <button
              type="button"
              onClick={() => {
                setShowNutritionSummary(!showNutritionSummary);
                setShowTemplateList(false);
                setShowTemplateForm(false);
              }}
              className="comic-button px-4 py-2 bg-accent text-accent-foreground flex items-center gap-2"
            >
              <Activity size={18} />
              NUTRITION
            </button>
            <button
              type="button"
              onClick={() => {
                setShowTemplateList(!showTemplateList);
                setShowTemplateForm(false);
                setShowNutritionSummary(false);
              }}
              className="comic-button px-4 py-2 bg-secondary text-secondary-foreground flex items-center gap-2"
            >
              <FileText size={18} />
              TEMPLATES
            </button>
            <button
              type="button"
              onClick={() => {
                setShowTemplateForm(!showTemplateForm);
                setShowTemplateList(false);
                setShowNutritionSummary(false);
              }}
              className="comic-button px-4 py-2 bg-primary text-primary-foreground flex items-center gap-2"
            >
              <Plus size={18} />
              CREATE TEMPLATE
            </button>
            <button
              type="button"
              onClick={handleExportICal}
              className="comic-button px-4 py-2 bg-accent text-accent-foreground flex items-center gap-2"
              disabled={!mealPlans || mealPlans.length === 0}
            >
              <Download size={18} />
              EXPORT ICAL
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 comic-panel bg-destructive text-destructive-foreground p-4 rounded-none font-bold">
            {error}
          </div>
        )}

        {/* Template Form */}
        <AnimatePresence>
          {showTemplateForm && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6"
            >
              <TemplateForm
                onSubmit={handleCreateTemplate}
                onCancel={() => setShowTemplateForm(false)}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Template List */}
        <AnimatePresence>
          {showTemplateList && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6"
            >
              <div className="comic-panel rounded-none p-6 bg-card">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-black uppercase tracking-wide">
                    MY TEMPLATES
                  </h2>
                  <button
                    type="button"
                    onClick={() => setShowTemplateList(false)}
                    className="comic-button p-2 bg-secondary text-secondary-foreground"
                    aria-label="Close"
                  >
                    <X size={20} />
                  </button>
                </div>
                <TemplateList
                  templates={templates}
                  onApply={handleApplyTemplate}
                  onDelete={handleDeleteTemplate}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Nutrition Summary */}
        <AnimatePresence>
          {showNutritionSummary && nutritionSummary && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6"
            >
              <div className="comic-panel rounded-none p-6 bg-card">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-black uppercase tracking-wide">
                    NUTRITION SUMMARY
                  </h2>
                  <button
                    type="button"
                    onClick={() => setShowNutritionSummary(false)}
                    className="comic-button p-2 bg-secondary text-secondary-foreground"
                    aria-label="Close"
                  >
                    <X size={20} />
                  </button>
                </div>
                <NutritionSummary
                  dailyTotals={nutritionSummary.daily_totals}
                  weeklyTotal={nutritionSummary.weekly_total}
                  missingNutritionCount={nutritionSummary.missing_nutrition_count}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className="flex gap-6">
          {/* Recipe Sidebar */}
          <AnimatePresence>
            {showSidebar && (
              <motion.aside
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="w-80 flex-shrink-0"
              >
                <div className="comic-panel rounded-none p-4 bg-card sticky top-8">
                  <h2 className="text-xl font-black uppercase tracking-wide mb-4">
                    RECIPES
                  </h2>
                  
                  {/* Search */}
                  <div className="mb-4">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={18} />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search recipes..."
                        className="w-full comic-input pl-10"
                      />
                    </div>
                  </div>

                  {/* Recipe List */}
                  <div className="space-y-2 max-h-[600px] overflow-y-auto">
                    {filteredRecipes.length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        {searchQuery ? 'No recipes found' : 'No recipes available'}
                      </p>
                    ) : (
                      filteredRecipes.map((recipe) => (
                        <div
                          key={recipe.id}
                          draggable
                          onDragStart={(e) => handleDragStart(e, recipe)}
                          onDragEnd={handleDragEnd}
                          className={`comic-border p-3 bg-background cursor-move hover:bg-primary/10 transition-colors ${
                            draggedRecipe?.id === recipe.id ? 'opacity-50' : ''
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            {recipe.image_url && (
                              <img
                                src={recipe.image_url}
                                alt={recipe.title}
                                className="w-12 h-12 object-cover rounded comic-border"
                              />
                            )}
                            <div className="flex-1 min-w-0">
                              <p className="font-bold text-sm truncate">{recipe.title}</p>
                              {recipe.tags && recipe.tags.length > 0 && (
                                <p className="text-xs text-muted-foreground truncate">
                                  {recipe.tags.join(', ')}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </motion.aside>
            )}
          </AnimatePresence>

          {/* Calendar */}
          <div className="flex-1">
            {mealPlans && mealPlans.length === 0 && !loading ? (
              <EmptyState
                icon={<Calendar size={64} strokeWidth={3} />}
                message="NO MEAL PLANS YET"
                description="Drag recipes from the sidebar onto the calendar to start planning your meals!"
                action={{
                  label: 'SHOW RECIPES',
                  onClick: () => setShowSidebar(true),
                }}
              />
            ) : (
              <MealPlannerCalendar
                mealPlans={mealPlans}
                onMealPlanUpdate={handleMealPlanUpdate}
                onMealPlanDelete={handleMealPlanDelete}
                onRecipeDrop={handleRecipeDrop}
              />
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
