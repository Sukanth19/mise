'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react';
import MealTimeSlot from './MealTimeSlot';
import { MealPlan, Recipe } from '@/types';

type ViewMode = 'week' | 'month';
type MealTime = 'breakfast' | 'lunch' | 'dinner' | 'snack';

interface MealPlannerCalendarProps {
  mealPlans: MealPlan[];
  onMealPlanUpdate: (mealPlanId: number, date: string, mealTime: MealTime) => void;
  onMealPlanDelete: (mealPlanId: number) => void;
  onRecipeDrop: (recipeId: number, date: string, mealTime: MealTime) => void;
}

const MEAL_TIMES: MealTime[] = ['breakfast', 'lunch', 'dinner', 'snack'];
const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export default function MealPlannerCalendar({
  mealPlans,
  onMealPlanUpdate,
  onMealPlanDelete,
  onRecipeDrop,
}: MealPlannerCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<ViewMode>('week');

  // Get the start of the week (Sunday)
  const getWeekStart = (date: Date) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day;
    return new Date(d.setDate(diff));
  };

  // Get the start of the month
  const getMonthStart = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  };

  // Get dates to display based on view mode
  const getDatesToDisplay = () => {
    if (viewMode === 'week') {
      const weekStart = getWeekStart(currentDate);
      return Array.from({ length: 7 }, (_, i) => {
        const date = new Date(weekStart);
        date.setDate(weekStart.getDate() + i);
        return date;
      });
    } else {
      // Month view - get all days in the month plus padding
      const monthStart = getMonthStart(currentDate);
      const firstDayOfWeek = monthStart.getDay();
      const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
      
      const dates: Date[] = [];
      
      // Add padding days from previous month
      for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        const date = new Date(monthStart);
        date.setDate(date.getDate() - i - 1);
        dates.push(date);
      }
      
      // Add days of current month
      for (let i = 0; i < daysInMonth; i++) {
        const date = new Date(monthStart);
        date.setDate(date.getDate() + i);
        dates.push(date);
      }
      
      // Add padding days from next month to complete the grid
      const remainingDays = 7 - (dates.length % 7);
      if (remainingDays < 7) {
        for (let i = 0; i < remainingDays; i++) {
          const date = new Date(monthStart);
          date.setDate(daysInMonth + i + 1);
          dates.push(date);
        }
      }
      
      return dates;
    }
  };

  const dates = getDatesToDisplay();

  // Navigate to previous period
  const goToPrevious = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setMonth(newDate.getMonth() - 1);
    }
    setCurrentDate(newDate);
  };

  // Navigate to next period
  const goToNext = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() + 7);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  // Go to today
  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Format date as YYYY-MM-DD
  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  // Get meal plans for a specific date and meal time
  const getMealPlansForSlot = (date: Date, mealTime: MealTime) => {
    const dateStr = formatDate(date);
    return mealPlans?.filter(
      (mp) => mp.meal_date === dateStr && mp.meal_time === mealTime
    ) || [];
  };

  // Format display date
  const getDisplayDate = () => {
    if (viewMode === 'week') {
      const weekStart = getWeekStart(currentDate);
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);
      return `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    } else {
      return currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    }
  };

  // Check if date is in current month (for month view styling)
  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === currentDate.getMonth();
  };

  // Check if date is today
  const isToday = (date: Date) => {
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  };

  return (
    <div className="space-y-4">
      {/* Header with navigation and view mode toggle */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={goToPrevious}
            className="comic-button p-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
            aria-label="Previous period"
          >
            <ChevronLeft size={20} />
          </button>
          <button
            type="button"
            onClick={goToToday}
            className="comic-button px-4 py-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
          >
            TODAY
          </button>
          <button
            type="button"
            onClick={goToNext}
            className="comic-button p-2 bg-secondary text-secondary-foreground hover:bg-secondary/80"
            aria-label="Next period"
          >
            <ChevronRight size={20} />
          </button>
        </div>

        <h2 className="text-xl font-black uppercase tracking-wide">
          {getDisplayDate()}
        </h2>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setViewMode('week')}
            className={`comic-button px-4 py-2 ${
              viewMode === 'week'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            WEEK
          </button>
          <button
            type="button"
            onClick={() => setViewMode('month')}
            className={`comic-button px-4 py-2 ${
              viewMode === 'month'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            MONTH
          </button>
        </div>
      </div>

      {/* Calendar grid */}
      <div className="comic-panel rounded-none p-4 bg-card">
        {viewMode === 'week' ? (
          // Week view - show all meal times for each day
          <div className="space-y-4">
            {dates.map((date, dateIndex) => (
              <motion.div
                key={formatDate(date)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: dateIndex * 0.05 }}
                className={`comic-border p-4 ${
                  isToday(date) ? 'bg-primary/10' : 'bg-background'
                }`}
              >
                <div className="font-black text-lg mb-3 uppercase tracking-wide">
                  {DAYS_OF_WEEK[date.getDay()]} {date.getDate()}
                  {isToday(date) && (
                    <span className="ml-2 text-sm text-primary">(TODAY)</span>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                  {MEAL_TIMES.map((mealTime) => (
                    <MealTimeSlot
                      key={`${formatDate(date)}-${mealTime}`}
                      date={formatDate(date)}
                      mealTime={mealTime}
                      mealPlans={getMealPlansForSlot(date, mealTime)}
                      onMealPlanUpdate={onMealPlanUpdate}
                      onMealPlanDelete={onMealPlanDelete}
                      onRecipeDrop={onRecipeDrop}
                    />
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          // Month view - compact grid
          <div>
            {/* Day headers */}
            <div className="grid grid-cols-7 gap-2 mb-2">
              {DAYS_OF_WEEK.map((day) => (
                <div
                  key={day}
                  className="text-center font-black text-sm uppercase tracking-wide p-2"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar grid */}
            <div className="grid grid-cols-7 gap-2">
              {dates.map((date, dateIndex) => (
                <motion.div
                  key={formatDate(date)}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: dateIndex * 0.01 }}
                  className={`comic-border min-h-[120px] p-2 ${
                    isToday(date)
                      ? 'bg-primary/10 border-primary'
                      : isCurrentMonth(date)
                      ? 'bg-background'
                      : 'bg-muted/50'
                  }`}
                >
                  <div
                    className={`font-bold text-sm mb-2 ${
                      isCurrentMonth(date) ? 'text-foreground' : 'text-muted-foreground'
                    }`}
                  >
                    {date.getDate()}
                  </div>
                  <div className="space-y-1">
                    {MEAL_TIMES.map((mealTime) => {
                      const plans = getMealPlansForSlot(date, mealTime);
                      if (plans.length === 0) return null;
                      return (
                        <div
                          key={`${formatDate(date)}-${mealTime}`}
                          className="text-xs font-bold truncate bg-primary/20 px-1 py-0.5 rounded"
                          title={`${mealTime}: ${plans.length} meal(s)`}
                        >
                          {plans.length} {mealTime.charAt(0).toUpperCase()}
                        </div>
                      );
                    })}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
