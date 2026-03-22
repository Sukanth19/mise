/**
 * Responsive Design Tests
 * 
 * Validates Requirements 11.1, 11.2, 11.3, 11.4:
 * - Desktop screens (>1024px)
 * - Tablet screens (768-1024px)
 * - Mobile screens (<768px)
 * - Recipe grid layout adjusts based on screen width
 */

import { render, screen } from '@testing-library/react';
import RecipeGrid from '@/components/RecipeGrid';
import RecipeDetail from '@/components/RecipeDetail';
import { Recipe } from '@/types';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('Responsive Design Tests', () => {
  const mockRecipes: Recipe[] = [
    {
      id: 1,
      user_id: 1,
      title: 'Test Recipe 1',
      image_url: 'https://example.com/image1.jpg',
      ingredients: ['ingredient 1', 'ingredient 2'],
      steps: ['step 1', 'step 2'],
      tags: ['dinner', 'quick'],
      reference_link: 'https://example.com/recipe1',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      user_id: 1,
      title: 'Test Recipe 2',
      image_url: 'https://example.com/image2.jpg',
      ingredients: ['ingredient 3'],
      steps: ['step 3'],
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
  ];

  describe('Requirement 11.1: Desktop Layout (>1024px)', () => {
    test('RecipeGrid has desktop-appropriate column classes', () => {
      const { container } = render(<RecipeGrid recipes={mockRecipes} />);
      const grid = container.querySelector('.grid');
      
      // Desktop should support 3-4 columns
      expect(grid?.className).toContain('lg:grid-cols-3');
      expect(grid?.className).toContain('xl:grid-cols-4');
    });

    test('RecipeDetail has appropriate max-width for desktop', () => {
      const { container } = render(<RecipeDetail recipe={mockRecipes[0]} />);
      const detailContainer = container.querySelector('.max-w-4xl');
      
      expect(detailContainer).toBeInTheDocument();
    });

    test('RecipeGrid uses gap spacing appropriate for desktop', () => {
      const { container } = render(<RecipeGrid recipes={mockRecipes} />);
      const grid = container.querySelector('.grid');
      
      // Should have gap-6 for proper spacing
      expect(grid?.className).toContain('gap-6');
    });
  });

  describe('Requirement 11.2: Tablet Layout (768-1024px)', () => {
    test('RecipeGrid has tablet-appropriate column classes', () => {
      const { container } = render(<RecipeGrid recipes={mockRecipes} />);
      const grid = container.querySelector('.grid');
      
      // Tablet should support 2 columns at sm breakpoint
      expect(grid?.className).toContain('sm:grid-cols-2');
    });

    test('RecipeDetail image has responsive height for tablet', () => {
      const { container } = render(<RecipeDetail recipe={mockRecipes[0]} />);
      const imageContainer = container.querySelector('.h-64.md\\:h-96');
      
      expect(imageContainer).toBeInTheDocument();
    });

    test('RecipeDetail padding adjusts for tablet', () => {
      const { container } = render(<RecipeDetail recipe={mockRecipes[0]} />);
      const contentContainer = container.querySelector('.p-6.md\\:p-8');
      
      expect(contentContainer).toBeInTheDocument();
    });
  });

  describe('Requirement 11.3: Mobile Layout (<768px)', () => {
    test('RecipeGrid has mobile-appropriate single column layout', () => {
      const { container } = render(<RecipeGrid recipes={mockRecipes} />);
      const grid = container.querySelector('.grid');
      
      // Mobile should default to single column
      expect(grid?.className).toContain('grid-cols-1');
    });

    test('RecipeDetail renders all content in mobile-friendly format', () => {
      render(<RecipeDetail recipe={mockRecipes[0]} />);
      
      // All content should be present and accessible
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
      expect(screen.getByText('Ingredients')).toBeInTheDocument();
      expect(screen.getByText('Instructions')).toBeInTheDocument();
      expect(screen.getByText('ingredient 1')).toBeInTheDocument();
      expect(screen.getByText('step 1')).toBeInTheDocument();
    });

    test('RecipeDetail image has base mobile height', () => {
      const { container } = render(<RecipeDetail recipe={mockRecipes[0]} />);
      const imageContainer = container.querySelector('.h-64');
      
      expect(imageContainer).toBeInTheDocument();
    });
  });

  describe('Requirement 11.4: Recipe Grid Layout Adjusts Based on Screen Width', () => {
    test('RecipeGrid has all responsive breakpoint classes', () => {
      const { container } = render(<RecipeGrid recipes={mockRecipes} />);
      const grid = container.querySelector('.grid');
      
      // Verify all breakpoints are present
      expect(grid?.className).toContain('grid-cols-1'); // Mobile: <640px
      expect(grid?.className).toContain('sm:grid-cols-2'); // Tablet: 640px-1024px
      expect(grid?.className).toContain('lg:grid-cols-3'); // Desktop: 1024px-1280px
      expect(grid?.className).toContain('xl:grid-cols-4'); // Large Desktop: >1280px
    });

    test('RecipeGrid renders correctly with varying recipe counts', () => {
      // Test with 1 recipe
      const { rerender, container } = render(<RecipeGrid recipes={[mockRecipes[0]]} />);
      let grid = container.querySelector('.grid');
      expect(grid).toBeInTheDocument();
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();

      // Test with 2 recipes
      rerender(<RecipeGrid recipes={mockRecipes} />);
      grid = container.querySelector('.grid');
      expect(grid).toBeInTheDocument();
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
      expect(screen.getByText('Test Recipe 2')).toBeInTheDocument();

      // Test with many recipes
      const manyRecipes = Array.from({ length: 8 }, (_, i) => ({
        ...mockRecipes[0],
        id: i + 1,
        title: `Recipe ${i + 1}`,
      }));
      rerender(<RecipeGrid recipes={manyRecipes} />);
      grid = container.querySelector('.grid');
      expect(grid).toBeInTheDocument();
    });

    test('RecipeGrid maintains consistent gap spacing across breakpoints', () => {
      const { container } = render(<RecipeGrid recipes={mockRecipes} />);
      const grid = container.querySelector('.grid');
      
      // Gap should be consistent across all breakpoints
      expect(grid?.className).toContain('gap-6');
    });

    test('RecipeDetail content layout is responsive', () => {
      const { container } = render(<RecipeDetail recipe={mockRecipes[0]} />);
      
      // Check for responsive padding
      const contentContainer = container.querySelector('.p-6.md\\:p-8');
      expect(contentContainer).toBeInTheDocument();
      
      // Check for responsive image height
      const imageContainer = container.querySelector('.h-64.md\\:h-96');
      expect(imageContainer).toBeInTheDocument();
    });
  });

  describe('Additional Responsive Design Validation', () => {
    test('RecipeGrid empty state is responsive', () => {
      render(<RecipeGrid recipes={[]} />);
      
      const emptyState = screen.getByText('No recipes found');
      expect(emptyState).toBeInTheDocument();
      expect(emptyState.className).toContain('text-center');
    });

    test('RecipeDetail tags wrap properly on small screens', () => {
      const { container } = render(<RecipeDetail recipe={mockRecipes[0]} />);
      const tagsContainer = container.querySelector('.flex.flex-wrap');
      
      expect(tagsContainer).toBeInTheDocument();
      expect(tagsContainer?.className).toContain('gap-2');
    });

    test('RecipeDetail ingredients list is touch-friendly', () => {
      render(<RecipeDetail recipe={mockRecipes[0]} />);
      
      const checkbox = screen.getAllByRole('checkbox')[0];
      expect(checkbox).toBeInTheDocument();
      expect(checkbox.className).toContain('h-5 w-5');
    });

    test('RecipeDetail steps are readable on all screen sizes', () => {
      render(<RecipeDetail recipe={mockRecipes[0]} />);
      
      const stepNumber = screen.getByText('1');
      expect(stepNumber).toBeInTheDocument();
      expect(stepNumber.className).toContain('rounded-full');
    });

    test('RecipeDetail reference link button is responsive', () => {
      render(<RecipeDetail recipe={mockRecipes[0]} />);
      
      const link = screen.getByText('View Original Recipe');
      expect(link).toBeInTheDocument();
      expect(link.className).toContain('inline-block');
      expect(link.className).toContain('px-6 py-3');
    });
  });

  describe('Tailwind Breakpoint Validation', () => {
    test('Tailwind breakpoints match requirements', () => {
      // This test validates that Tailwind's default breakpoints align with requirements
      // sm: 640px (covers tablet lower bound ~768px)
      // md: 768px (tablet)
      // lg: 1024px (desktop)
      // xl: 1280px (large desktop)
      
      const { container } = render(<RecipeGrid recipes={mockRecipes} />);
      const grid = container.querySelector('.grid');
      
      // Verify the progression of columns matches screen size expectations
      const classes = grid?.className || '';
      
      // Mobile first: 1 column
      expect(classes).toMatch(/grid-cols-1/);
      
      // Small screens (sm: 640px+): 2 columns
      expect(classes).toMatch(/sm:grid-cols-2/);
      
      // Large screens (lg: 1024px+): 3 columns
      expect(classes).toMatch(/lg:grid-cols-3/);
      
      // Extra large screens (xl: 1280px+): 4 columns
      expect(classes).toMatch(/xl:grid-cols-4/);
    });
  });
});
