import { render, screen, fireEvent } from '@testing-library/react';
import RecipePreviewModal from './RecipePreviewModal';
import { Recipe } from '@/types';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('RecipePreviewModal', () => {
  const mockRecipe: Recipe = {
    id: 1,
    user_id: 1,
    title: 'Test Recipe',
    image_url: '/uploads/test.jpg',
    ingredients: ['Ingredient 1', 'Ingredient 2', 'Ingredient 3'],
    steps: ['Step 1', 'Step 2', 'Step 3'],
    tags: ['tag1', 'tag2'],
    reference_link: 'https://example.com',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  const mockOnClose = jest.fn();
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('does not render when isOpen is false', () => {
    render(
      <RecipePreviewModal
        isOpen={false}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.queryByText('Test Recipe')).not.toBeInTheDocument();
  });

  it('does not render when recipe is null', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={null}
      />
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('renders modal with recipe details when isOpen is true', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 1')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 2')).toBeInTheDocument();
    expect(screen.getByText('Ingredient 3')).toBeInTheDocument();
    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 2')).toBeInTheDocument();
    expect(screen.getByText('Step 3')).toBeInTheDocument();
  });

  it('displays recipe tags', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.getByText('tag1')).toBeInTheDocument();
    expect(screen.getByText('tag2')).toBeInTheDocument();
  });

  it('displays recipe image when image_url is provided', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    const image = screen.getByAltText('Test Recipe');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'http://localhost:8000/uploads/test.jpg');
  });

  it('does not display image when image_url is not provided', () => {
    const recipeWithoutImage = { ...mockRecipe, image_url: undefined };
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={recipeWithoutImage}
      />
    );

    expect(screen.queryByAltText('Test Recipe')).not.toBeInTheDocument();
  });

  it('calls onClose when Close button is clicked', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    const closeButton = screen.getByText('CLOSE');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when backdrop is clicked', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    const backdrop = screen.getByRole('dialog').previousSibling as HTMLElement;
    fireEvent.click(backdrop);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('displays Edit button when onEdit is provided', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
        onEdit={mockOnEdit}
      />
    );

    expect(screen.getByText('EDIT')).toBeInTheDocument();
  });

  it('does not display Edit button when onEdit is not provided', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.queryByText('EDIT')).not.toBeInTheDocument();
  });

  it('calls onEdit and onClose when Edit button is clicked', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
        onEdit={mockOnEdit}
      />
    );

    const editButton = screen.getByText('EDIT');
    fireEvent.click(editButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
    expect(mockOnEdit).toHaveBeenCalledTimes(1);
  });

  it('displays Delete button when onDelete is provided', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('DELETE')).toBeInTheDocument();
  });

  it('does not display Delete button when onDelete is not provided', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.queryByText('DELETE')).not.toBeInTheDocument();
  });

  it('calls onDelete when Delete button is clicked', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByText('DELETE');
    fireEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledTimes(1);
  });

  it('has proper ARIA attributes for accessibility', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'recipe-preview-title');
  });

  it('renders ingredients section with proper heading', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.getByText('Ingredients')).toBeInTheDocument();
  });

  it('renders instructions section with proper heading', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.getByText('Instructions')).toBeInTheDocument();
  });

  it('renders step numbers correctly', () => {
    render(
      <RecipePreviewModal
        isOpen={true}
        onClose={mockOnClose}
        recipe={mockRecipe}
      />
    );

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });
});
