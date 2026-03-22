import { render, screen } from '@testing-library/react';
import RecipeGrid from './RecipeGrid';
import { Recipe } from '@/types';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('RecipeGrid Unit Tests', () => {
  const mockRecipes: Recipe[] = [
    {
      id: 1,
      user_id: 1,
      title: 'Recipe 1',
      image_url: 'https://example.com/image1.jpg',
      ingredients: ['ingredient 1'],
      steps: ['step 1'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      user_id: 1,
      title: 'Recipe 2',
      image_url: 'https://example.com/image2.jpg',
      ingredients: ['ingredient 2'],
      steps: ['step 2'],
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
    {
      id: 3,
      user_id: 1,
      title: 'Recipe 3',
      ingredients: ['ingredient 3'],
      steps: ['step 3'],
      created_at: '2024-01-03T00:00:00Z',
      updated_at: '2024-01-03T00:00:00Z',
    },
  ];

  test('renders multiple recipe cards', () => {
    render(<RecipeGrid recipes={mockRecipes} />);
    
    expect(screen.getByText('Recipe 1')).toBeInTheDocument();
    expect(screen.getByText('Recipe 2')).toBeInTheDocument();
    expect(screen.getByText('Recipe 3')).toBeInTheDocument();
  });

  test('displays empty state when no recipes', () => {
    render(<RecipeGrid recipes={[]} />);
    
    expect(screen.getByText('No recipes found')).toBeInTheDocument();
  });

  test('has responsive grid layout classes', () => {
    const { container } = render(<RecipeGrid recipes={mockRecipes} />);
    
    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
    
    // Check for responsive column classes
    expect(grid?.className).toContain('grid-cols-1'); // mobile
    expect(grid?.className).toContain('sm:grid-cols-2'); // tablet
    expect(grid?.className).toContain('lg:grid-cols-3'); // desktop
    expect(grid?.className).toContain('xl:grid-cols-4'); // large desktop
  });

  test('renders single recipe', () => {
    const singleRecipe = [mockRecipes[0]];
    render(<RecipeGrid recipes={singleRecipe} />);
    
    expect(screen.getByText('Recipe 1')).toBeInTheDocument();
    expect(screen.queryByText('Recipe 2')).not.toBeInTheDocument();
  });

  test('renders many recipes', () => {
    const manyRecipes: Recipe[] = Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      user_id: 1,
      title: `Recipe ${i + 1}`,
      ingredients: ['ingredient'],
      steps: ['step'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }));
    
    render(<RecipeGrid recipes={manyRecipes} />);
    
    manyRecipes.forEach((recipe) => {
      expect(screen.getByText(recipe.title)).toBeInTheDocument();
    });
  });
});
