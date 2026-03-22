import { render } from '@testing-library/react';
import fc from 'fast-check';
import RecipeCard from './RecipeCard';
import { Recipe } from '@/types';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Feature: recipe-saver, Property 13: Recipe cards display required information
describe('RecipeCard Property Tests', () => {
  test('recipe cards contain title and image reference', () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.integer({ min: 1 }),
          user_id: fc.integer({ min: 1 }),
          title: fc.string({ minLength: 1, maxLength: 100 }),
          image_url: fc.option(fc.webUrl(), { nil: undefined }),
          ingredients: fc.array(fc.string({ minLength: 1 }), { minLength: 1 }),
          steps: fc.array(fc.string({ minLength: 1 }), { minLength: 1 }),
          tags: fc.option(fc.array(fc.string()), { nil: undefined }),
          reference_link: fc.option(fc.webUrl(), { nil: undefined }),
          created_at: fc.date().map(d => d.toISOString()),
          updated_at: fc.date().map(d => d.toISOString()),
        }),
        (recipe: Recipe) => {
          const { container } = render(<RecipeCard recipe={recipe} />);
          
          // **Validates: Requirements 5.3**
          // Recipe card must display title
          expect(container.textContent).toContain(recipe.title);
          
          // Recipe card must have image element (either img or placeholder)
          const hasImage = container.querySelector('img') !== null;
          const hasPlaceholder = container.textContent?.includes('No Image');
          expect(hasImage || hasPlaceholder).toBe(true);
          
          // If image_url is provided, img element should have src attribute
          if (recipe.image_url) {
            const imgElement = container.querySelector('img');
            expect(imgElement).not.toBeNull();
            expect(imgElement?.getAttribute('src')).toBe(recipe.image_url);
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
