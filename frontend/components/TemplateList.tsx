'use client';

import { motion } from 'framer-motion';
import { Calendar, Trash2, FileText } from 'lucide-react';
import { MealPlanTemplate } from '@/types';

interface TemplateListProps {
  templates: MealPlanTemplate[];
  onApply: (templateId: number) => void;
  onDelete: (templateId: number) => void;
}

export default function TemplateList({ templates, onApply, onDelete }: TemplateListProps) {
  if (templates.length === 0) {
    return (
      <div className="comic-panel rounded-none p-8 bg-card text-center">
        <FileText size={48} className="mx-auto mb-4 text-muted-foreground" strokeWidth={3} />
        <p className="font-bold text-muted-foreground mb-2">No templates yet</p>
        <p className="text-sm text-muted-foreground">
          Create a template to quickly apply meal plans
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {templates.map((template, index) => (
        <motion.div
          key={template.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          className="comic-panel rounded-none p-4 bg-card hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all duration-100"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-black uppercase tracking-wide mb-2">
                {template.name}
              </h3>
              {template.description && (
                <p className="text-sm text-muted-foreground mb-3 font-medium">
                  {template.description}
                </p>
              )}
              <div className="flex items-center gap-4 text-sm">
                <span className="font-bold text-muted-foreground">
                  {template.items.length} {template.items.length === 1 ? 'RECIPE' : 'RECIPES'}
                </span>
                <span className="text-muted-foreground">
                  {Math.max(...template.items.map((item) => item.day_offset)) + 1} DAYS
                </span>
              </div>

              {/* Preview of template items */}
              <div className="mt-3 space-y-1">
                {template.items.slice(0, 3).map((item, idx) => (
                  <div
                    key={idx}
                    className="text-xs font-medium text-muted-foreground flex items-center gap-2"
                  >
                    <span className="font-bold">Day {item.day_offset + 1}</span>
                    <span>•</span>
                    <span className="capitalize">{item.meal_time}</span>
                    <span>•</span>
                    <span className="truncate">{item.recipe?.title || 'Recipe'}</span>
                  </div>
                ))}
                {template.items.length > 3 && (
                  <div className="text-xs font-medium text-muted-foreground">
                    + {template.items.length - 3} more...
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <button
                type="button"
                onClick={() => onApply(template.id)}
                className="comic-button px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/80 flex items-center gap-2 whitespace-nowrap"
                aria-label={`Apply ${template.name}`}
              >
                <Calendar size={16} />
                APPLY
              </button>
              <button
                type="button"
                onClick={() => onDelete(template.id)}
                className="comic-button px-4 py-2 bg-destructive text-destructive-foreground hover:bg-destructive/80 flex items-center gap-2 whitespace-nowrap"
                aria-label={`Delete ${template.name}`}
              >
                <Trash2 size={16} />
                DELETE
              </button>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
