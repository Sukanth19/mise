import { render, screen, fireEvent } from '@testing-library/react';
import PrintView from './PrintView';
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

  // Mock window.print
  const mockPrint = jest.fn();
  beforeAll(() => {
    window.print = mockPrint;
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders print button', () => {
    render(<PrintView recipe={mockRecipe} />);

    const printButton = screen.getByRole('button', { name: /print recipe/i });
    expect(printButton).toBeInTheDocument();
    expect(printButton).toHaveTextContent('PRINT RECIPE');
  });

  it('calls window.print when print button is clicked', () => {
    render(<PrintView recipe={mockRecipe} />);

    const printButton = screen.getByRole('button', { name: /print recipe/i });
    fireEvent.click(printButton);

    expect(mockPrint).toHaveBeenCalledTimes(1);
  });

  it('renders recipe title', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
  });

  it('renders all ingredients', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Ingredient 1')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 2')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 3')).toBeInTheDocument();
  });

  it('renders all steps', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 2')).toBeInTheDocument();
    expect(screen.getByText('Step 3')).toBeInTheDocument();
  });

  it('renders tags when provided', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText(/tag1, tag2/)).toBeInTheDocument();
  });

  it('does not render tags section when tags are not provided', () => {
    const recipeWithoutTags = { ...mockRecipe, tags: undefined };
    render(<PrintView recipe={recipeWithoutTags} />);

    expect(screen.queryByText(/Tags:/)).not.toBeInTheDocument();
  });

  it('renders recipe image when image_url is provided', () => {
    render(<PrintView recipe={mockRecipe} />);

    const image = screen.getByAltText('Test Recipe');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'http://localhost:8000/uploads/test.jpg');
  });

  it('does not render image when image_url is not provided', () => {
    const recipeWithoutImage = { ...mockRecipe, image_url: undefined };
    render(<PrintView recipe={recipeWithoutImage} />);

    expect(screen.queryByAltText('Test Recipe')).not.toBeInTheDocument();
  });

  it('renders reference link when provided', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText(/Source:/)).toBeInTheDocument();
    expect(screen.getByText('https://example.com/recipe')).toBeInTheDocument();
  });

  it('does not render reference link section when not provided', () => {
    const recipeWithoutLink = { ...mockRecipe, reference_link: undefined };
    render(<PrintView recipe={recipeWithoutLink} />);

    expect(screen.queryByText(/Source:/)).not.toBeInTheDocument();
  });

  it('renders Ingredients heading', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Ingredients')).toBeInTheDocument();
  });

  it('renders Instructions heading', () => {
    render(<PrintView recipe={mockRecipe} />);

    expect(screen.getByText('Instructions')).toBeInTheDocument();
  });

  it('renders step numbers correctly', () => {
    render(<PrintView recipe={mockRecipe} />);

    // Check for step numbers in the format "1.", "2.", "3."
    expect(screen.getByText('1.')).toBeInTheDocument();
    expect(screen.getByText('2.')).toBeInTheDocument();
    expect(screen.getByText('3.')).toBeInTheDocument();
  });

  it('has print-view class for styling', () => {
    const { container } = render(<PrintView recipe={mockRecipe} />);

    expect(container.querySelector('.print-view')).toBeInTheDocument();
  });

  it('renders print button with print:hidden class', () => {
    const { container } = render(<PrintView recipe={mockRecipe} />);

    const buttonContainer = container.querySelector('.print\\:hidden');
    expect(buttonContainer).toBeInTheDocument();
  });
});
