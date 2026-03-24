'use client';

import { motion } from 'framer-motion';

export function RecipeCardSkeleton() {
  return (
    <div className="comic-panel rounded-none overflow-hidden">
      <div className="relative w-full h-48 bg-muted border-b-4 border-border skeleton" />
      <div className="p-4 bg-card">
        <div className="h-6 bg-muted skeleton rounded w-3/4" />
      </div>
    </div>
  );
}

export function RecipeGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.05 }}
        >
          <RecipeCardSkeleton />
        </motion.div>
      ))}
    </div>
  );
}

export function RecipeDetailSkeleton() {
  return (
    <div className="max-w-4xl mx-auto comic-panel overflow-hidden">
      <div className="w-full h-64 md:h-96 bg-muted skeleton" />
      <div className="p-6 md:p-8 space-y-6">
        <div className="h-10 bg-muted skeleton rounded w-2/3" />
        <div className="flex gap-2">
          <div className="h-8 w-20 bg-muted skeleton rounded" />
          <div className="h-8 w-24 bg-muted skeleton rounded" />
        </div>
        <div className="space-y-4">
          <div className="h-8 bg-muted skeleton rounded w-1/4" />
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-6 bg-muted skeleton rounded w-full" />
          ))}
        </div>
        <div className="space-y-4">
          <div className="h-8 bg-muted skeleton rounded w-1/4" />
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-16 bg-muted skeleton rounded w-full" />
          ))}
        </div>
      </div>
    </div>
  );
}

export function CollectionCardSkeleton() {
  return (
    <div className="comic-panel rounded-none overflow-hidden">
      <div className="relative w-full h-48 bg-muted border-b-4 border-border skeleton" />
      <div className="p-4 bg-card space-y-2">
        <div className="h-6 bg-muted skeleton rounded w-3/4" />
        <div className="h-4 bg-muted skeleton rounded w-1/2" />
      </div>
    </div>
  );
}

export function CollectionGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.05 }}
        >
          <CollectionCardSkeleton />
        </motion.div>
      ))}
    </div>
  );
}

export function MealPlanCardSkeleton() {
  return (
    <div className="comic-panel rounded-none p-4 bg-card space-y-3">
      <div className="flex items-center justify-between">
        <div className="h-5 bg-muted skeleton rounded w-24" />
        <div className="h-5 bg-muted skeleton rounded w-16" />
      </div>
      <div className="h-32 bg-muted skeleton rounded" />
      <div className="h-6 bg-muted skeleton rounded w-2/3" />
    </div>
  );
}

export function MealPlanGridSkeleton({ count = 7 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.05 }}
        >
          <MealPlanCardSkeleton />
        </motion.div>
      ))}
    </div>
  );
}
