import { render } from '@testing-library/react';
import fc from 'fast-check';
import RecipeDetail from './RecipeDetail';
import { Recipe } from '@/types';

// Feature: recipe-saver, Property 14: Recipe details contain all fields
describe('RecipeDetail Property Tests', () => {
  test('recipe details contain all required fields', () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.integer({ min: 1 }),
          user_id: fc.integer({ min: 1 }),
          title: fc.string({ minLength: 1, maxLength: 100 }),
          image_url: fc.option(fc.webUrl(), { nil: undefined }),
          ingredients: fc.array(fc.string({ minLength: 1, maxLength: 50 }), { minLength: 1, maxLength: 20 }),
          steps: fc.array(fc.string({ minLength: 1, maxLength: 100 }), { minLength: 1, maxLength: 15 }),
          tags: fc.option(fc.array(fc.string({ minLength: 1, maxLength: 20 }), { maxLength: 10 }), { nil: undefined }),
          reference_link: fc.option(fc.webUrl(), { nil: undefined }),
          created_at: fc.date().map(d => d.toISOString()),
          updated_at: fc.date().map(d => d.toISOString()),
        }),
        (recipe: Recipe) => {
          const { container } = render(<RecipeDetail recipe={recipe} />);
          
          // **Validates: Requirements 6.2, 6.4, 6.5**
          
          // Must display title
          expect(container.textContent).toContain(recipe.title);
          
          // Must display all ingredients
          recipe.ingredients.forEach((ingredient) => {
            expect(container.textContent).toContain(ingredient);
          });
          
          // Must display all steps in order
          recipe.steps.forEach((step) => {
            expect(container.textContent).toContain(step);
          });
          
          // If image_url is present, must display image
          if (recipe.image_url) {
            const imgElement = container.querySelector('img');
            expect(imgElement).not.toBeNull();
            expect(imgElement?.getAttribute('src')).toBe(recipe.image_url);
          }
          
          // If tags are present, must display them
          if (recipe.tags && recipe.tags.length > 0) {
            recipe.tags.forEach((tag) => {
              expect(container.textContent).toContain(tag);
            });
          }
          
          // If reference_link is present, must display it as clickable link
          if (recipe.reference_link) {
            const links = container.querySelectorAll('a');
            const linkElement = Array.from(links).find(
              link => link.getAttribute('href') === recipe.reference_link
            );
            expect(linkElement).toBeDefined();
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
