'use client';

import { useState } from 'react';

const DIETARY_LABELS = [
  { value: 'vegan', label: 'Vegan', emoji: '🌱' },
  { value: 'vegetarian', label: 'Vegetarian', emoji: '🥗' },
  { value: 'gluten-free', label: 'Gluten-Free', emoji: '🌾' },
  { value: 'dairy-free', label: 'Dairy-Free', emoji: '🥛' },
  { value: 'keto', label: 'Keto', emoji: '🥑' },
  { value: 'paleo', label: 'Paleo', emoji: '🍖' },
  { value: 'low-carb', label: 'Low-Carb', emoji: '🥦' },
];

interface DietaryLabelsSelectorProps {
  selectedLabels: string[];
  onChange: (labels: string[]) => void;
  disabled?: boolean;
}

export default function DietaryLabelsSelector({ 
  selectedLabels, 
  onChange,
  disabled = false 
}: DietaryLabelsSelectorProps) {
  const handleToggle = (value: string) => {
    if (disabled) return;
    
    if (selectedLabels.includes(value)) {
      onChange(selectedLabels.filter(label => label !== value));
    } else {
      onChange([...selectedLabels, value]);
    }
  };

  return (
    <div className="space-y-3">
      <label className="block font-bold uppercase text-sm text-foreground">
        Dietary Labels
      </label>
      <div className="flex flex-wrap gap-2">
        {DIETARY_LABELS.map(({ value, label, emoji }) => (
          <button
            key={value}
            type="button"
            onClick={() => handleToggle(value)}
            disabled={disabled}
            className={`px-4 py-2 text-sm font-bold uppercase rounded-none transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              selectedLabels.includes(value)
                ? 'bg-secondary text-secondary-foreground comic-border'
                : 'bg-muted text-muted-foreground border-2 border-border hover:bg-muted/80'
            }`}
            aria-pressed={selectedLabels.includes(value) ? "true" : "false"}
          >
            <span className="mr-2">{emoji}</span>
            {label}
          </button>
        ))}
      </div>
      {selectedLabels.length > 0 && (
        <p className="text-xs text-muted-foreground font-medium">
          {selectedLabels.length} label{selectedLabels.length !== 1 ? 's' : ''} selected
        </p>
      )}
    </div>
  );
}
