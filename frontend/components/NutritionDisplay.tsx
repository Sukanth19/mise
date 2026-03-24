'use client';

export interface NutritionFacts {
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fat_g?: number;
  fiber_g?: number;
}

interface NutritionDisplayProps {
  nutritionFacts: NutritionFacts | null;
  perServing?: NutritionFacts | null;
  servings?: number;
  showPerServing?: boolean;
}

export default function NutritionDisplay({ 
  nutritionFacts, 
  perServing,
  servings,
  showPerServing = true 
}: NutritionDisplayProps) {
  if (!nutritionFacts) {
    return (
      <div className="comic-panel bg-muted p-6 rounded-none">
        <p className="text-muted-foreground font-medium text-center">
          No nutrition information available
        </p>
      </div>
    );
  }

  const formatValue = (value?: number): string => {
    if (value === undefined || value === null) return '-';
    return value.toFixed(1);
  };

  const hasAnyValue = nutritionFacts.calories !== undefined || 
                      nutritionFacts.protein_g !== undefined ||
                      nutritionFacts.carbs_g !== undefined ||
                      nutritionFacts.fat_g !== undefined ||
                      nutritionFacts.fiber_g !== undefined;

  if (!hasAnyValue) {
    return (
      <div className="comic-panel bg-muted p-6 rounded-none">
        <p className="text-muted-foreground font-medium text-center">
          No nutrition information available
        </p>
      </div>
    );
  }

  return (
    <div className="comic-panel bg-card p-6 rounded-none space-y-6">
      <h3 className="text-xl font-black uppercase text-foreground border-b-4 border-border pb-2">
        NUTRITION FACTS
      </h3>

      {/* Total Nutrition */}
      <div>
        <h4 className="text-sm font-bold uppercase text-muted-foreground mb-3">
          Total Recipe {servings && `(${servings} servings)`}
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <NutritionItem label="Calories" value={formatValue(nutritionFacts.calories)} unit="" />
          <NutritionItem label="Protein" value={formatValue(nutritionFacts.protein_g)} unit="g" />
          <NutritionItem label="Carbs" value={formatValue(nutritionFacts.carbs_g)} unit="g" />
          <NutritionItem label="Fat" value={formatValue(nutritionFacts.fat_g)} unit="g" />
          <NutritionItem label="Fiber" value={formatValue(nutritionFacts.fiber_g)} unit="g" />
        </div>
      </div>

      {/* Per Serving Nutrition */}
      {showPerServing && perServing && (
        <div className="border-t-4 border-border pt-4">
          <h4 className="text-sm font-bold uppercase text-muted-foreground mb-3">
            Per Serving
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <NutritionItem label="Calories" value={formatValue(perServing.calories)} unit="" highlight />
            <NutritionItem label="Protein" value={formatValue(perServing.protein_g)} unit="g" highlight />
            <NutritionItem label="Carbs" value={formatValue(perServing.carbs_g)} unit="g" highlight />
            <NutritionItem label="Fat" value={formatValue(perServing.fat_g)} unit="g" highlight />
            <NutritionItem label="Fiber" value={formatValue(perServing.fiber_g)} unit="g" highlight />
          </div>
        </div>
      )}
    </div>
  );
}

interface NutritionItemProps {
  label: string;
  value: string;
  unit: string;
  highlight?: boolean;
}

function NutritionItem({ label, value, unit, highlight }: NutritionItemProps) {
  return (
    <div className={`comic-border p-3 ${highlight ? 'bg-primary/10' : 'bg-muted'}`}>
      <div className="text-xs font-bold uppercase text-muted-foreground mb-1">
        {label}
      </div>
      <div className="text-lg font-black text-foreground">
        {value}{unit && <span className="text-sm ml-1">{unit}</span>}
      </div>
    </div>
  );
}
