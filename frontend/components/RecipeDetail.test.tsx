import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RecipeDetail from './RecipeDetail';
import { Recipe } from '@/types';

// Use manual mock for RatingStars
jest.mock('./RatingStars');

// Mock apiClient
jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
}));

const { apiClient } = require('@/lib/api');

describe('RecipeDetail Unit Tests', () => {
  const completeRecipe: Recipe = {
    id: 1,
    user_id: 1,
    title: 'Complete Recipe',
    image_url: 'https://example.com/image.jpg',
    ingredients: ['2 cups flour', '1 cup sugar', '3 eggs'],
    steps: ['Mix dry ingredients', 'Add wet ingredients', 'Bake at 350°F'],
    tags: ['dessert', 'baking'],
    reference_link: 'https://example.com/original-recipe',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock the rating API call to return 404 (no rating yet)
    apiClient.mockRejectedValue(new Error('Not found'));
  });

  test('renders complete recipe with all fields', () => {
    const { container } = render(<RecipeDetail recipe={completeRecipe} />);
    
    // Title
    expect(screen.getByText('Complete Recipe')).toBeInTheDocument();
    
    // Image
    const img = container.querySelector('img');
    expect(img).toBeInTheDocument();
    expect(img?.getAttribute('src')).toBe('https://example.com/image.jpg');
    
    // Ingredients
    expect(screen.getByText('Ingredients')).toBeInTheDocument();
    expect(screen.getByText('2 cups flour')).toBeInTheDocument();
    expect(screen.getByText('1 cup sugar')).toBeInTheDocument();
    expect(screen.getByText('3 eggs')).toBeInTheDocument();
    
    // Steps
    expect(screen.getByText('Instructions')).toBeInTheDocument();
    expect(screen.getByText('Mix dry ingredients')).toBeInTheDocument();
    expect(screen.getByText('Add wet ingredients')).toBeInTheDocument();
    expect(screen.getByText('Bake at 350°F')).toBeInTheDocument();
    
    // Tags
    expect(screen.getByText('dessert')).toBeInTheDocument();
    expect(screen.getByText('baking')).toBeInTheDocument();
    
    // Reference link
    const link = screen.getByText('View Original Recipe');
    expect(link).toBeInTheDocument();
    expect(link.getAttribute('href')).toBe('https://example.com/original-recipe');
  });

  test('renders recipe without optional fields', () => {
    const minimalRecipe: Recipe = {
      id: 2,
      user_id: 1,
      title: 'Minimal Recipe',
      ingredients: ['ingredient 1'],
      steps: ['step 1'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    
    const { container } = render(<RecipeDetail recipe={minimalRecipe} />);
    
    // Title
    expect(screen.getByText('Minimal Recipe')).toBeInTheDocument();
    
    // No image
    expect(container.querySelector('img')).not.toBeInTheDocument();
    
    // Ingredients and steps still present
    expect(screen.getByText('ingredient 1')).toBeInTheDocument();
    expect(screen.getByText('step 1')).toBeInTheDocument();
    
    // No tags or reference link
    expect(screen.queryByText('View Original Recipe')).not.toBeInTheDocument();
  });

  test('ingredient checkboxes toggle correctly', () => {
    render(<RecipeDetail recipe={completeRecipe} />);
    
    const checkbox = screen.getByLabelText('2 cups flour') as HTMLInputElement;
    expect(checkbox.checked).toBe(false);
    
    // Check the checkbox
    fireEvent.click(checkbox);
    expect(checkbox.checked).toBe(true);
    
    // Uncheck the checkbox
    fireEvent.click(checkbox);
    expect(checkbox.checked).toBe(false);
  });

  test('multiple ingredients can be checked independently', () => {
    render(<RecipeDetail recipe={completeRecipe} />);
    
    const checkbox1 = screen.getByLabelText('2 cups flour') as HTMLInputElement;
    const checkbox2 = screen.getByLabelText('1 cup sugar') as HTMLInputElement;
    const checkbox3 = screen.getByLabelText('3 eggs') as HTMLInputElement;
    
    fireEvent.click(checkbox1);
    fireEvent.click(checkbox3);
    
    expect(checkbox1.checked).toBe(true);
    expect(checkbox2.checked).toBe(false);
    expect(checkbox3.checked).toBe(true);
  });

  test('steps are rendered in correct order', () => {
    render(<RecipeDetail recipe={completeRecipe} />);
    
    const stepNumbers = screen.getAllByText(/^[1-3]$/);
    expect(stepNumbers).toHaveLength(3);
    expect(stepNumbers[0].textContent).toBe('1');
    expect(stepNumbers[1].textContent).toBe('2');
    expect(stepNumbers[2].textContent).toBe('3');
  });

  test('reference link opens in new tab', () => {
    render(<RecipeDetail recipe={completeRecipe} />);
    
    const link = screen.getByText('View Original Recipe');
    expect(link.getAttribute('target')).toBe('_blank');
    expect(link.getAttribute('rel')).toBe('noopener noreferrer');
  });

  test('renders recipe with empty tags array', () => {
    const recipeWithEmptyTags = { ...completeRecipe, tags: [] };
    render(<RecipeDetail recipe={recipeWithEmptyTags} />);
    
    expect(screen.getByText('Complete Recipe')).toBeInTheDocument();
    // Tags section should not be rendered
    const tagElements = screen.queryAllByText(/dessert|baking/);
    expect(tagElements).toHaveLength(0);
  });

  test('renders recipe with single ingredient and step', () => {
    const simpleRecipe: Recipe = {
      id: 3,
      user_id: 1,
      title: 'Simple Recipe',
      ingredients: ['water'],
      steps: ['boil water'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };
    
    render(<RecipeDetail recipe={simpleRecipe} />);
    
    expect(screen.getByText('water')).toBeInTheDocument();
    expect(screen.getByText('boil water')).toBeInTheDocument();
  });
});
