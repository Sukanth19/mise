'use client';

const ALLERGENS = [
  { value: 'nuts', label: 'Nuts', emoji: '🥜' },
  { value: 'dairy', label: 'Dairy', emoji: '🥛' },
  { value: 'eggs', label: 'Eggs', emoji: '🥚' },
  { value: 'soy', label: 'Soy', emoji: '🫘' },
  { value: 'wheat', label: 'Wheat', emoji: '🌾' },
  { value: 'fish', label: 'Fish', emoji: '🐟' },
  { value: 'shellfish', label: 'Shellfish', emoji: '🦐' },
];

interface AllergenWarningsProps {
  selectedAllergens: string[];
  onChange?: (allergens: string[]) => void;
  displayMode?: 'selector' | 'display';
  disabled?: boolean;
}

export default function AllergenWarnings({ 
  selectedAllergens, 
  onChange,
  displayMode = 'selector',
  disabled = false 
}: AllergenWarningsProps) {
  const handleToggle = (value: string) => {
    if (disabled || !onChange) return;
    
    if (selectedAllergens.includes(value)) {
      onChange(selectedAllergens.filter(allergen => allergen !== value));
    } else {
      onChange([...selectedAllergens, value]);
    }
  };

  // Display mode - show prominent warnings
  if (displayMode === 'display') {
    if (selectedAllergens.length === 0) {
      return null;
    }

    return (
      <div className="comic-border bg-destructive/10 border-destructive p-4 rounded-none">
        <div className="flex items-start gap-3">
          <div className="text-2xl">⚠️</div>
          <div className="flex-1">
            <h3 className="text-lg font-black uppercase text-destructive mb-2">
              ALLERGEN WARNING
            </h3>
            <div className="flex flex-wrap gap-2">
              {selectedAllergens.map(allergen => {
                const allergenInfo = ALLERGENS.find(a => a.value === allergen);
                return (
                  <span
                    key={allergen}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-destructive text-destructive-foreground font-bold uppercase text-sm rounded-none"
                  >
                    {allergenInfo?.emoji} {allergenInfo?.label || allergen}
                  </span>
                );
              })}
            </div>
            <p className="mt-2 text-sm font-medium text-destructive">
              This recipe contains ingredients that may cause allergic reactions.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Selector mode - allow editing
  return (
    <div className="space-y-3">
      <label className="block font-bold uppercase text-sm text-foreground">
        Allergen Warnings
      </label>
      <div className="flex flex-wrap gap-2">
        {ALLERGENS.map(({ value, label, emoji }) => (
          <button
            key={value}
            type="button"
            onClick={() => handleToggle(value)}
            disabled={disabled}
            className={`px-4 py-2 text-sm font-bold uppercase rounded-none transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              selectedAllergens.includes(value)
                ? 'bg-destructive text-destructive-foreground comic-border'
                : 'bg-muted text-muted-foreground border-2 border-border hover:bg-muted/80'
            }`}
            aria-pressed={selectedAllergens.includes(value) ? "true" : "false"}
          >
            <span className="mr-2">{emoji}</span>
            {label}
          </button>
        ))}
      </div>
      {selectedAllergens.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-destructive font-bold">
          <span>⚠️</span>
          <span>
            {selectedAllergens.length} allergen{selectedAllergens.length !== 1 ? 's' : ''} marked
          </span>
        </div>
      )}
    </div>
  );
}
