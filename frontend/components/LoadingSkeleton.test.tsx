import { render, screen } from '@testing-library/react';
import {
  RecipeCardSkeleton,
  RecipeGridSkeleton,
  RecipeDetailSkeleton,
  CollectionCardSkeleton,
  CollectionGridSkeleton,
  MealPlanCardSkeleton,
  MealPlanGridSkeleton,
} from './LoadingSkeleton';

describe('LoadingSkeleton', () => {
  describe('RecipeCardSkeleton', () => {
    it('renders skeleton for recipe card', () => {
      const { container } = render(<RecipeCardSkeleton />);
      expect(container.querySelector('.skeleton')).toBeInTheDocument();
      expect(container.querySelector('.comic-panel')).toBeInTheDocument();
    });
  });

  describe('RecipeGridSkeleton', () => {
    it('renders default count of 8 skeletons', () => {
      const { container } = render(<RecipeGridSkeleton />);
      const skeletons = container.querySelectorAll('.comic-panel');
      expect(skeletons).toHaveLength(8);
    });

    it('renders custom count of skeletons', () => {
      const { container } = render(<RecipeGridSkeleton count={4} />);
      const skeletons = container.querySelectorAll('.comic-panel');
      expect(skeletons).toHaveLength(4);
    });
  });

  describe('RecipeDetailSkeleton', () => {
    it('renders skeleton for recipe detail', () => {
      const { container } = render(<RecipeDetailSkeleton />);
      expect(container.querySelector('.skeleton')).toBeInTheDocument();
      expect(container.querySelector('.comic-panel')).toBeInTheDocument();
    });
  });

  describe('CollectionCardSkeleton', () => {
    it('renders skeleton for collection card', () => {
      const { container } = render(<CollectionCardSkeleton />);
      expect(container.querySelector('.skeleton')).toBeInTheDocument();
      expect(container.querySelector('.comic-panel')).toBeInTheDocument();
    });
  });

  describe('CollectionGridSkeleton', () => {
    it('renders default count of 6 skeletons', () => {
      const { container } = render(<CollectionGridSkeleton />);
      const skeletons = container.querySelectorAll('.comic-panel');
      expect(skeletons).toHaveLength(6);
    });

    it('renders custom count of skeletons', () => {
      const { container } = render(<CollectionGridSkeleton count={3} />);
      const skeletons = container.querySelectorAll('.comic-panel');
      expect(skeletons).toHaveLength(3);
    });
  });

  describe('MealPlanCardSkeleton', () => {
    it('renders skeleton for meal plan card', () => {
      const { container } = render(<MealPlanCardSkeleton />);
      expect(container.querySelector('.skeleton')).toBeInTheDocument();
      expect(container.querySelector('.comic-panel')).toBeInTheDocument();
    });
  });

  describe('MealPlanGridSkeleton', () => {
    it('renders default count of 7 skeletons', () => {
      const { container } = render(<MealPlanGridSkeleton />);
      const skeletons = container.querySelectorAll('.comic-panel');
      expect(skeletons).toHaveLength(7);
    });

    it('renders custom count of skeletons', () => {
      const { container } = render(<MealPlanGridSkeleton count={5} />);
      const skeletons = container.querySelectorAll('.comic-panel');
      expect(skeletons).toHaveLength(5);
    });
  });
});
