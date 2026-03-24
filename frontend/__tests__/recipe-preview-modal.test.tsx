import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import RecipePreviewModal from '@/components/RecipePreviewModal';
import { Recipe } from '@/types';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

describe('RecipePreviewModal', () => {
  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  };

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
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  /**
   * Unit test: Modal renders when open
   */
  test('renders modal when isOpen is true', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 1')).toBeInTheDocument();
    expect(screen.getByText('Step 1')).toBeInTheDocument();
  });

  /**
   * Unit test: Modal does not render when closed
   */
  test('does not render modal when isOpen is false', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={false}
        onClose={jest.fn()}
      />
    );

    expect(screen.queryByText('Test Recipe')).not.toBeInTheDocument();
  });

  /**
   * Unit test: Modal does not render when recipe is null
   */
  test('does not render modal when recipe is null', () => {
    render(
      <RecipePreviewModal
        recipe={null}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.queryByText('Test Recipe')).not.toBeInTheDocument();
  });

  /**
   * Unit test: Close button calls onClose
   */
  test('close button calls onClose handler', () => {
    const onClose = jest.fn();
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={onClose}
      />
    );

    const closeButton = screen.getByLabelText('Close preview');
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  /**
   * Unit test: Backdrop click calls onClose
   */
  test('clicking backdrop calls onClose handler', () => {
    const onClose = jest.fn();
    const { container } = render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={onClose}
      />
    );

    // Find the backdrop (first child of the modal container)
    const backdrop = container.querySelector('.bg-black.bg-opacity-50');
    expect(backdrop).toBeInTheDocument();
    
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(onClose).toHaveBeenCalledTimes(1);
    }
  });

  /**
   * Unit test: Displays recipe image
   */
  test('displays recipe image when image_url is provided', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    const image = screen.getByAltText('Test Recipe');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'http://localhost:8000/uploads/test.jpg');
  });

  /**
   * Unit test: Does not display image when image_url is missing
   */
  test('does not display image when image_url is not provided', () => {
    const recipeWithoutImage = { ...mockRecipe, image_url: undefined };
    render(
      <RecipePreviewModal
        recipe={recipeWithoutImage}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    const image = screen.queryByAltText('Test Recipe');
    expect(image).not.toBeInTheDocument();
  });

  /**
   * Unit test: Displays all tags
   */
  test('displays all recipe tags', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('tag1')).toBeInTheDocument();
    expect(screen.getByText('tag2')).toBeInTheDocument();
  });

  /**
   * Unit test: Displays all ingredients
   */
  test('displays all recipe ingredients', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('Ingredient 1')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 2')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 3')).toBeInTheDocument();
  });

  /**
   * Unit test: Displays all steps
   */
  test('displays all recipe steps', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 2')).toBeInTheDocument();
    expect(screen.getByText('Step 3')).toBeInTheDocument();
  });

  /**
   * Unit test: Displays reference link
   */
  test('displays reference link when provided', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    const link = screen.getByText('View Original Recipe →');
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://example.com/recipe');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  /**
   * Unit test: Edit button navigates to edit page
   */
  test('edit button navigates to edit page and closes modal', () => {
    const onClose = jest.fn();
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={onClose}
      />
    );

    const editButton = screen.getByText('EDIT');
    fireEvent.click(editButton);

    expect(mockRouter.push).toHaveBeenCalledWith('/recipes/1/edit');
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  /**
   * Unit test: Delete button calls onDelete handler
   */
  test('delete button calls onDelete handler and closes modal', () => {
    const onClose = jest.fn();
    const onDelete = jest.fn();
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={onClose}
        onDelete={onDelete}
      />
    );

    const deleteButton = screen.getByText('DELETE');
    fireEvent.click(deleteButton);

    expect(onDelete).toHaveBeenCalledWith(1);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  /**
   * Unit test: Delete button not shown when onDelete is not provided
   */
  test('delete button is not shown when onDelete is not provided', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.queryByText('DELETE')).not.toBeInTheDocument();
  });

  /**
   * Unit test: Modal has proper ARIA label for close button
   */
  test('close button has proper aria-label', () => {
    render(
      <RecipePreviewModal
        recipe={mockRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    const closeButton = screen.getByLabelText('Close preview');
    expect(closeButton).toBeInTheDocument();
  });

  /**
   * Unit test: Modal content is scrollable
   */
  test('modal content is scrollable for long recipes', () => {
    const longRecipe: Recipe = {
      ...mockRecipe,
      ingredients: Array(50).fill('Ingredient'),
      steps: Array(50).fill('Step'),
    };

    const { container } = render(
      <RecipePreviewModal
        recipe={longRecipe}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    const modalContent = container.querySelector('.max-h-\\[90vh\\]');
    expect(modalContent).toBeInTheDocument();
    expect(modalContent).toHaveClass('overflow-y-auto');
  });
});
