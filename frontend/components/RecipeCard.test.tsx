import { render, screen, fireEvent } from '@testing-library/react';
import RecipeCard from './RecipeCard';
import { Recipe } from '@/types';

// Mock next/navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('RecipeCard Unit Tests', () => {
  const mockRecipe: Recipe = {
    id: 1,
    user_id: 1,
    title: 'Test Recipe',
    image_url: 'https://example.com/image.jpg',
    ingredients: ['ingredient 1', 'ingredient 2'],
    steps: ['step 1', 'step 2'],
    tags: ['tag1', 'tag2'],
    reference_link: 'https://example.com/recipe',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    mockPush.mockClear();
  });

  test('renders recipe with image and title', () => {
    const { container } = render(<RecipeCard recipe={mockRecipe} />);
    
    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    
    const img = container.querySelector('img');
    expect(img).toBeInTheDocument();
    expect(img?.getAttribute('src')).toBe('https://example.com/image.jpg');
    expect(img?.getAttribute('alt')).toBe('Test Recipe');
  });

  test('renders recipe without image (shows placeholder)', () => {
    const recipeWithoutImage = { ...mockRecipe, image_url: undefined };
    const { container } = render(<RecipeCard recipe={recipeWithoutImage} />);
    
    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    expect(screen.getByText('No Image')).toBeInTheDocument();
    expect(container.querySelector('img')).not.toBeInTheDocument();
  });

  test('navigates to recipe detail page on click', () => {
    render(<RecipeCard recipe={mockRecipe} />);
    
    const card = screen.getByRole('button');
    fireEvent.click(card);
    
    expect(mockPush).toHaveBeenCalledWith('/recipes/1');
  });

  test('navigates to recipe detail page on Enter key', () => {
    render(<RecipeCard recipe={mockRecipe} />);
    
    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: 'Enter' });
    
    expect(mockPush).toHaveBeenCalledWith('/recipes/1');
  });

  test('navigates to recipe detail page on Space key', () => {
    render(<RecipeCard recipe={mockRecipe} />);
    
    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: ' ' });
    
    expect(mockPush).toHaveBeenCalledWith('/recipes/1');
  });

  test('has hover animation classes', () => {
    const { container } = render(<RecipeCard recipe={mockRecipe} />);
    
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('hover:scale-105');
    expect(card.className).toContain('hover:shadow-lg');
    expect(card.className).toContain('transition-transform');
    expect(card.className).toContain('duration-300');
  });

  test('truncates long titles', () => {
    const longTitleRecipe = {
      ...mockRecipe,
      title: 'This is a very long recipe title that should be truncated to fit in the card',
    };
    const { container } = render(<RecipeCard recipe={longTitleRecipe} />);
    
    const titleElement = container.querySelector('h3');
    expect(titleElement?.className).toContain('truncate');
  });
});
