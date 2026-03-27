'use client';

import { useState } from 'react';
import LoadingSpinner from '@/components/LoadingSpinner';
import LoginAnimation from '@/components/LoginAnimation';
import { 
  RecipeGridSkeleton, 
  RecipeDetailSkeleton,
  CollectionGridSkeleton 
} from '@/components/LoadingSkeleton';

export default function AnimationsDemoPage() {
  const [showLogin, setShowLogin] = useState(false);

  return (
    <div className="container mx-auto p-6 space-y-12">
      <div className="comic-panel p-6 rounded-none">
        <h1 className="comic-heading text-4xl mb-4">Animation Components Demo</h1>
        <p className="comic-text text-muted-foreground">
          Preview all available loading animations and their variants
        </p>
      </div>

      {/* Login Animation */}
      <section className="space-y-4">
        <h2 className="comic-heading text-2xl">Login Animation</h2>
        <div className="comic-panel p-12 rounded-none flex items-center justify-center min-h-[300px]">
          {showLogin ? (
            <LoginAnimation />
          ) : (
            <button
              onClick={() => setShowLogin(true)}
              className="comic-button bg-primary text-primary-foreground py-3 px-6 rounded-none"
            >
              Show Login Animation
            </button>
          )}
        </div>
        {showLogin && (
          <button
            onClick={() => setShowLogin(false)}
            className="comic-button bg-secondary text-secondary-foreground py-2 px-4 rounded-none text-sm"
          >
            Reset
          </button>
        )}
      </section>

      {/* Loading Spinner Variants */}
      <section className="space-y-4">
        <h2 className="comic-heading text-2xl">Loading Spinner Variants</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Default */}
          <div className="comic-panel p-8 rounded-none">
            <h3 className="comic-label mb-4">Default (Utensils)</h3>
            <div className="flex items-center justify-center min-h-[200px]">
              <LoadingSpinner variant="default" size="lg" text="Loading..." />
            </div>
          </div>

          {/* Recipe */}
          <div className="comic-panel p-8 rounded-none">
            <h3 className="comic-label mb-4">Recipe (Cooking Pot)</h3>
            <div className="flex items-center justify-center min-h-[200px]">
              <LoadingSpinner variant="recipe" size="lg" text="Cooking..." />
            </div>
          </div>

          {/* Collection */}
          <div className="comic-panel p-8 rounded-none">
            <h3 className="comic-label mb-4">Collection (Book)</h3>
            <div className="flex items-center justify-center min-h-[200px]">
              <LoadingSpinner variant="collection" size="lg" text="Loading collections..." />
            </div>
          </div>

          {/* Minimal */}
          <div className="comic-panel p-8 rounded-none">
            <h3 className="comic-label mb-4">Minimal</h3>
            <div className="flex items-center justify-center min-h-[200px]">
              <LoadingSpinner variant="minimal" size="lg" text="Please wait..." />
            </div>
          </div>
        </div>
      </section>

      {/* Sizes */}
      <section className="space-y-4">
        <h2 className="comic-heading text-2xl">Spinner Sizes</h2>
        <div className="comic-panel p-8 rounded-none">
          <div className="flex items-center justify-around gap-8 flex-wrap">
            <div className="text-center">
              <p className="comic-label mb-4">Small</p>
              <LoadingSpinner variant="default" size="sm" />
            </div>
            <div className="text-center">
              <p className="comic-label mb-4">Medium</p>
              <LoadingSpinner variant="default" size="md" />
            </div>
            <div className="text-center">
              <p className="comic-label mb-4">Large</p>
              <LoadingSpinner variant="default" size="lg" />
            </div>
          </div>
        </div>
      </section>

      {/* Skeleton Loaders */}
      <section className="space-y-4">
        <h2 className="comic-heading text-2xl">Skeleton Loaders</h2>
        
        <div className="space-y-8">
          <div>
            <h3 className="comic-label mb-4">Recipe Grid Skeleton</h3>
            <RecipeGridSkeleton count={4} />
          </div>

          <div>
            <h3 className="comic-label mb-4">Collection Grid Skeleton</h3>
            <CollectionGridSkeleton count={3} />
          </div>

          <div>
            <h3 className="comic-label mb-4">Recipe Detail Skeleton</h3>
            <RecipeDetailSkeleton />
          </div>
        </div>
      </section>

      {/* CSS Animations */}
      <section className="space-y-4">
        <h2 className="comic-heading text-2xl">CSS Animation Classes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="comic-panel p-6 rounded-none text-center">
            <p className="comic-label mb-2">animate-shake</p>
            <div className="comic-button bg-destructive text-destructive-foreground py-2 px-4 rounded-none animate-shake">
              Error!
            </div>
          </div>

          <div className="comic-panel p-6 rounded-none text-center">
            <p className="comic-label mb-2">animate-pulse-scale</p>
            <div className="comic-button bg-primary text-primary-foreground py-2 px-4 rounded-none animate-pulse-scale">
              Pulsing
            </div>
          </div>

          <div className="comic-panel p-6 rounded-none text-center">
            <p className="comic-label mb-2">animate-pop-in</p>
            <div className="comic-button bg-accent text-accent-foreground py-2 px-4 rounded-none animate-pop-in">
              Pop In
            </div>
          </div>

          <div className="comic-panel p-6 rounded-none text-center">
            <p className="comic-label mb-2">animate-bounce-subtle</p>
            <div className="comic-button bg-secondary text-secondary-foreground py-2 px-4 rounded-none animate-bounce-subtle">
              Bouncing
            </div>
          </div>

          <div className="comic-panel p-6 rounded-none text-center">
            <p className="comic-label mb-2">animate-fade-in</p>
            <div className="comic-button bg-primary text-primary-foreground py-2 px-4 rounded-none animate-fade-in">
              Fade In
            </div>
          </div>

          <div className="comic-panel p-6 rounded-none text-center">
            <p className="comic-label mb-2">animate-slide-up</p>
            <div className="comic-button bg-accent text-accent-foreground py-2 px-4 rounded-none animate-slide-up">
              Slide Up
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
