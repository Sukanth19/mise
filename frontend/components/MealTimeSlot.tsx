'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import MealPlanCard from './MealPlanCard';
import { MealPlan } from '@/types';

type MealTime = 'breakfast' | 'lunch' | 'dinner' | 'snack';

interface MealTimeSlotProps {
  date: string;
  mealTime: MealTime;
  mealPlans: MealPlan[];
  onMealPlanUpdate: (mealPlanId: number, date: string, mealTime: MealTime) => void;
  onMealPlanDelete: (mealPlanId: number) => void;
  onRecipeDrop: (recipeId: number, date: string, mealTime: MealTime) => void;
}

const MEAL_TIME_LABELS: Record<MealTime, string> = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  dinner: 'Dinner',
  snack: 'Snack',
};

const MEAL_TIME_ICONS: Record<MealTime, string> = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙',
  snack: '🍎',
};

export default function MealTimeSlot({
  date,
  mealTime,
  mealPlans,
  onMealPlanUpdate,
  onMealPlanDelete,
  onRecipeDrop,
}: MealTimeSlotProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    try {
      const data = JSON.parse(e.dataTransfer.getData('application/json'));
      
      if (data.type === 'recipe') {
        // Dropping a recipe from the sidebar
        onRecipeDrop(data.recipeId, date, mealTime);
      } else if (data.type === 'meal-plan') {
        // Moving an existing meal plan
        onMealPlanUpdate(data.mealPlanId, date, mealTime);
      }
    } catch (error) {
      console.error('Error handling drop:', error);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`comic-border p-3 min-h-[100px] transition-all ${
        isDragOver
          ? 'bg-primary/20 border-primary border-4'
          : 'bg-background border-border'
      }`}
    >
      {/* Meal time header */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg" role="img" aria-label={mealTime}>
          {MEAL_TIME_ICONS[mealTime]}
        </span>
        <h4 className="font-black text-sm uppercase tracking-wide">
          {MEAL_TIME_LABELS[mealTime]}
        </h4>
      </div>

      {/* Meal plans */}
      <div className="space-y-2">
        {mealPlans.length > 0 ? (
          mealPlans.map((mealPlan, index) => (
            <motion.div
              key={mealPlan.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <MealPlanCard
                mealPlan={mealPlan}
                onDelete={onMealPlanDelete}
              />
            </motion.div>
          ))
        ) : (
          <div
            className={`text-center py-4 text-sm font-medium transition-opacity ${
              isDragOver ? 'opacity-100 text-primary' : 'opacity-50 text-muted-foreground'
            }`}
          >
            {isDragOver ? 'Drop here' : 'Drag recipe here'}
          </div>
        )}
      </div>
    </div>
  );
}
