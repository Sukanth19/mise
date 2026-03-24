import { render, screen, fireEvent } from '@testing-library/react';
import PrintView from '@/components/PrintView';
import { Recipe } from '@/types';

describe('PrintView', () => {
  const mockRecipe: Recipe = {
    id: 1,
    user_id: 1,
    title: 'Test Recipe',
    image_url: '/uploads/test.jpg',
    ingredients: ['Ingredient 1', 'Ingredient 2', 'Ingredient 3'],
    steps: ['Step 1', 'Step 2', 'Step 3'],
    tags: ['tag1', 'tag2'],
    reference_link: 'https://example.com/recipe',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    // Mock window.print
    window.print = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Unit test: Renders print button
   */
  test('renders print button', () => {
    render(<PrintView recipe={mockRecipe} />);

    const printButton = screen.getByLabelText('Print recipe');
    expect(printButton).toBeInTheDocument();
    expect(printButton).toHaveTextContent('🖨️ PRINT RECIPE');
  });

  /**
   * Unit test: Print button calls window.print
   */
  test('print button calls window.print when clicked', () => {
    render(<PrintView recipe={mockRecipe} />);

    const printButton = screen.getByLabelText('Print recipe');
    fireEvent.click(printButton);

    expect(window.print).toHaveBeenCalledTimes(1);
  });

  /**
   * Unit test: Renders recipe title
   */
  test('renders recipe title', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
  });

  /**
   * Unit test: Renders recipe image
   */
  test('renders recipe image when image_url is provided', () => {
    render(<PrintView recipe={mockRecipe} />);

    const image = screen.getByAltText('Test Recipe');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'http://localhost:8000/uploads/test.jpg');
  });

  /**
   * Unit test: Does not render image when image_url is missing
   */
  test('does not render image when image_url is not provided', () => {
    const recipeWithoutImage = { ...mockRecipe, image_url: undefined };
    render(<PrintView recipe={recipeWithoutImage} />);

    const image = screen.queryByAltText('Test Recipe');
    expect(image).not.toBeInTheDocument();
  });

  /**
   * Unit test: Renders all tags
   */
  test('renders all recipe tags', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText(/Tags:/)).toBeInTheDocument();
    expect(screen.getByText(/tag1, tag2/)).toBeInTheDocument();
  });

  /**
   * Unit test: Does not render tags section when no tags
   */
  test('does not render tags section when recipe has no tags', () => {
    const recipeWithoutTags = { ...mockRecipe, tags: undefined };
    render(<PrintView recipe={recipeWithoutTags} />);

    expect(screen.queryByText(/Tags:/)).not.toBeInTheDocument();
  });

  /**
   * Unit test: Renders all ingredients
   */
  test('renders all recipe ingredients', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Ingredients')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 1')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 2')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 3')).toBeInTheDocument();
  });

  /**
   * Unit test: Renders all steps
   */
  test('renders all recipe steps', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Instructions')).toBeInTheDocument();
    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 2')).toBeInTheDocument();
    expect(screen.getByText('Step 3')).toBeInTheDocument();
  });

  /**
   * Unit test: Renders reference link
   */
  test('renders reference link when provided', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText(/Source:/)).toBeInTheDocument();
    expect(screen.getByText(/https:\/\/example\.com\/recipe/)).toBeInTheDocument();
  });

  /**
   * Unit test: Does not render reference link when not provided
   */
  test('does not render reference link when not provided', () => {
    const recipeWithoutLink = { ...mockRecipe, reference_link: undefined };
    render(<PrintView recipe={recipeWithoutLink} />);

    expect(screen.queryByText(/Source:/)).not.toBeInTheDocument();
  });

  /**
   * Unit test: Print view has correct structure
   */
  test('print view has correct structure with print-view class', () => {
    const { container } = render(<PrintView recipe={mockRecipe} />);

    const printView = container.querySelector('.print-view');
    expect(printView).toBeInTheDocument();
  });

  /**
   * Unit test: Print button has print:hidden class
   */
  test('print button container has print:hidden class', () => {
    const { container } = render(<PrintView recipe={mockRecipe} />);

    const buttonContainer = container.querySelector('.print\\:hidden');
    expect(buttonContainer).toBeInTheDocument();
  });

  /**
   * Unit test: Ingredients are rendered as list items
   */
  test('ingredients are rendered as list items with bullets', () => {
    const { container } = render(<PrintView recipe={mockRecipe} />);

    const ingredientsList = container.querySelector('ul');
    expect(ingredientsList).toBeInTheDocument();
    
    const listItems = ingredientsList?.querySelectorAll('li');
    expect(listItems).toHaveLength(3);
  });

  /**
   * Unit test: Steps are rendered as ordered list
   */
  test('steps are rendered as ordered list with numbers', () => {
    const { container } = render(<PrintView recipe={mockRecipe} />);

    const stepsList = container.querySelector('ol');
    expect(stepsList).toBeInTheDocument();
    
    const listItems = stepsList?.querySelectorAll('li');
    expect(listItems).toHaveLength(3);
  });

  /**
   * Unit test: Print styles are injected
   */
  test('print-specific styles are injected into the page', () => {
    const { container } = render(<PrintView recipe={mockRecipe} />);

    // styled-jsx injects styles differently, check for the print-view class instead
    const printView = container.querySelector('.print-view');
    expect(printView).toBeInTheDocument();
  });

  /**
   * Unit test: Recipe with empty ingredients array
   */
  test('handles recipe with empty ingredients array', () => {
    const recipeWithNoIngredients = { ...mockRecipe, ingredients: [] };
    render(<PrintView recipe={recipeWithNoIngredients} />);

    expect(screen.getByText('Ingredients')).toBeInTheDocument();
    const { container } = render(<PrintView recipe={recipeWithNoIngredients} />);
    const ingredientsList = container.querySelector('ul');
    const listItems = ingredientsList?.querySelectorAll('li');
    expect(listItems).toHaveLength(0);
  });

  /**
   * Unit test: Recipe with empty steps array
   */
  test('handles recipe with empty steps array', () => {
    const recipeWithNoSteps = { ...mockRecipe, steps: [] };
    render(<PrintView recipe={recipeWithNoSteps} />);

    expect(screen.getByText('Instructions')).toBeInTheDocument();
    const { container } = render(<PrintView recipe={recipeWithNoSteps} />);
    const stepsList = container.querySelector('ol');
    const listItems = stepsList?.querySelectorAll('li');
    expect(listItems).toHaveLength(0);
  });

  /**
   * Unit test: Long recipe content renders correctly
   */
  test('renders long recipe with many ingredients and steps', () => {
    const longRecipe: Recipe = {
      ...mockRecipe,
      ingredients: Array(20).fill(0).map((_, i) => `Ingredient ${i + 1}`),
      steps: Array(15).fill(0).map((_, i) => `Step ${i + 1}`),
    };

    const { container } = render(<PrintView recipe={longRecipe} />);

    const ingredientsList = container.querySelector('ul');
    const ingredientItems = ingredientsList?.querySelectorAll('li');
    expect(ingredientItems).toHaveLength(20);

    const stepsList = container.querySelector('ol');
    const stepItems = stepsList?.querySelectorAll('li');
    expect(stepItems).toHaveLength(15);
  });
});
