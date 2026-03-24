'use client';

export interface DailyNutrition {
  date: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}

export interface WeeklyNutrition {
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
}

interface NutritionSummaryProps {
  dailyTotals: DailyNutrition[];
  weeklyTotal: WeeklyNutrition;
  missingNutritionCount: number;
}

export default function NutritionSummary({ 
  dailyTotals, 
  weeklyTotal,
  missingNutritionCount 
}: NutritionSummaryProps) {
  const formatValue = (value?: number): string => {
    if (value === undefined || value === null) return '-';
    return value.toFixed(1);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div className="space-y-6">
      {/* Missing Nutrition Warning */}
      {missingNutritionCount > 0 && (
        <div className="comic-border bg-warning/10 border-warning p-4 rounded-none">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚠️</span>
            <p className="font-bold text-warning">
              {missingNutritionCount} recipe{missingNutritionCount !== 1 ? 's' : ''} in this meal plan {missingNutritionCount !== 1 ? 'are' : 'is'} missing nutrition information and excluded from totals.
            </p>
          </div>
        </div>
      )}

      {/* Weekly Total */}
      <div className="comic-panel bg-primary/10 p-6 rounded-none">
        <h3 className="text-xl font-black uppercase text-foreground mb-4 border-b-4 border-border pb-2">
          WEEKLY TOTAL
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <SummaryItem label="Calories" value={formatValue(weeklyTotal.calories)} unit="" />
          <SummaryItem label="Protein" value={formatValue(weeklyTotal.protein_g)} unit="g" />
          <SummaryItem label="Carbs" value={formatValue(weeklyTotal.carbs_g)} unit="g" />
          <SummaryItem label="Fat" value={formatValue(weeklyTotal.fat_g)} unit="g" />
          <SummaryItem label="Fiber" value={formatValue(weeklyTotal.fiber_g)} unit="g" />
        </div>
      </div>

      {/* Daily Breakdown */}
      <div className="comic-panel bg-card p-6 rounded-none">
        <h3 className="text-xl font-black uppercase text-foreground mb-4 border-b-4 border-border pb-2">
          DAILY BREAKDOWN
        </h3>
        
        {dailyTotals.length === 0 ? (
          <p className="text-muted-foreground font-medium text-center py-8">
            No meal plan data for this period
          </p>
        ) : (
          <div className="space-y-4">
            {dailyTotals.map((day) => (
              <div key={day.date} className="border-2 border-border p-4">
                <h4 className="font-black uppercase text-sm text-muted-foreground mb-3">
                  {formatDate(day.date)}
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  <DailyItem label="Cal" value={formatValue(day.calories)} />
                  <DailyItem label="Protein" value={formatValue(day.protein_g)} unit="g" />
                  <DailyItem label="Carbs" value={formatValue(day.carbs_g)} unit="g" />
                  <DailyItem label="Fat" value={formatValue(day.fat_g)} unit="g" />
                  <DailyItem label="Fiber" value={formatValue(day.fiber_g)} unit="g" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface SummaryItemProps {
  label: string;
  value: string;
  unit: string;
}

function SummaryItem({ label, value, unit }: SummaryItemProps) {
  return (
    <div className="text-center">
      <div className="text-xs font-bold uppercase text-muted-foreground mb-1">
        {label}
      </div>
      <div className="text-2xl font-black text-foreground">
        {value}
        {unit && <span className="text-sm ml-1">{unit}</span>}
      </div>
    </div>
  );
}

interface DailyItemProps {
  label: string;
  value: string;
  unit?: string;
}

function DailyItem({ label, value, unit }: DailyItemProps) {
  return (
    <div className="bg-muted p-2">
      <div className="text-xs font-bold uppercase text-muted-foreground">
        {label}
      </div>
      <div className="text-lg font-black text-foreground">
        {value}
        {unit && <span className="text-xs ml-1">{unit}</span>}
      </div>
    </div>
  );
}
