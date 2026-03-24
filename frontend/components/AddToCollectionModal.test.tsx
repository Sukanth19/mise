import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AddToCollectionModal from './AddToCollectionModal';
import { Collection } from '@/types';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

const mockCollections: Collection[] = [
  {
    id: 1,
    user_id: 1,
    name: 'Breakfast Recipes',
    description: 'Morning meals',
    nesting_level: 0,
    recipe_count: 10,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    user_id: 1,
    name: 'Dinner Recipes',
    nesting_level: 0,
    recipe_count: 15,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 3,
    user_id: 1,
    name: 'Desserts',
    parent_collection_id: 2,
    nesting_level: 1,
    recipe_count: 5,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

describe('AddToCollectionModal', () => {
  test('does not render when isOpen is false', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={false}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    expect(screen.queryByText(/add to collections/i)).not.toBeInTheDocument();
  });

  test('renders when isOpen is true', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    expect(screen.getByText(/add to collections/i)).toBeInTheDocument();
  });

  test('displays all collections', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    expect(screen.getByText('Breakfast Recipes')).toBeInTheDocument();
    expect(screen.getByText('Dinner Recipes')).toBeInTheDocument();
    expect(screen.getByText('Desserts')).toBeInTheDocument();
  });

  test('displays recipe title when provided', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
        recipeTitle="Chocolate Cake"
      />
    );
    
    expect(screen.getByText(/chocolate cake/i)).toBeInTheDocument();
  });

  test('toggles collection selection', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const breakfastButton = screen.getByRole('button', { name: /breakfast recipes/i });
    
    // Initially not selected
    expect(breakfastButton).not.toHaveClass('bg-primary');
    
    // Click to select
    fireEvent.click(breakfastButton);
    expect(breakfastButton).toHaveClass('bg-primary');
    
    // Click again to deselect
    fireEvent.click(breakfastButton);
    expect(breakfastButton).not.toHaveClass('bg-primary');
  });

  test('allows multiple collection selection', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const breakfastButton = screen.getByRole('button', { name: /breakfast recipes/i });
    const dinnerButton = screen.getByRole('button', { name: /dinner recipes/i });
    
    fireEvent.click(breakfastButton);
    fireEvent.click(dinnerButton);
    
    expect(breakfastButton).toHaveClass('bg-primary');
    expect(dinnerButton).toHaveClass('bg-primary');
  });

  test('shows error when submitting without selection', async () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const submitButton = screen.getByRole('button', { name: /add to/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/please select at least one collection/i)).toBeInTheDocument();
    });
    
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('submits selected collections', async () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const breakfastButton = screen.getByRole('button', { name: /breakfast recipes/i });
    const dinnerButton = screen.getByRole('button', { name: /dinner recipes/i });
    
    fireEvent.click(breakfastButton);
    fireEvent.click(dinnerButton);
    
    const submitButton = screen.getByRole('button', { name: /add to 2 collections/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith([1, 2]);
      expect(onClose).toHaveBeenCalled();
    });
  });

  test('pre-selects collections from initialSelectedIds', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
        initialSelectedIds={[1, 3]}
      />
    );
    
    const breakfastButton = screen.getByRole('button', { name: /breakfast recipes/i });
    const dessertsButton = screen.getByRole('button', { name: /desserts/i });
    
    expect(breakfastButton).toHaveClass('bg-primary');
    expect(dessertsButton).toHaveClass('bg-primary');
  });

  test('closes modal when cancel button is clicked', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    expect(onClose).toHaveBeenCalled();
  });

  test('closes modal when close icon is clicked', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const closeButton = screen.getByLabelText(/close modal/i);
    fireEvent.click(closeButton);
    
    expect(onClose).toHaveBeenCalled();
  });

  test('shows empty state when no collections', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={[]}
      />
    );
    
    expect(screen.getByText(/no collections yet/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /add to/i })).not.toBeInTheDocument();
  });

  test('displays nested collection with indentation', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    // Desserts is nested (level 1), should have padding
    const dessertsButton = screen.getByRole('button', { name: /desserts/i });
    const dessertsDiv = dessertsButton.querySelector('div.pl-6');
    expect(dessertsDiv).toBeInTheDocument();
  });

  test('disables submit button while submitting', async () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const breakfastButton = screen.getByRole('button', { name: /breakfast recipes/i });
    fireEvent.click(breakfastButton);
    
    const submitButton = screen.getByRole('button', { name: /add to 1 collection/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/adding/i)).toBeInTheDocument();
    });
  });

  test('updates button text based on selection count', () => {
    const onClose = jest.fn();
    const onSubmit = jest.fn();
    
    render(
      <AddToCollectionModal
        isOpen={true}
        onClose={onClose}
        onSubmit={onSubmit}
        collections={mockCollections}
      />
    );
    
    const breakfastButton = screen.getByRole('button', { name: /breakfast recipes/i });
    const dinnerButton = screen.getByRole('button', { name: /dinner recipes/i });
    
    // Select one
    fireEvent.click(breakfastButton);
    expect(screen.getByRole('button', { name: /add to 1 collection$/i })).toBeInTheDocument();
    
    // Select two
    fireEvent.click(dinnerButton);
    expect(screen.getByRole('button', { name: /add to 2 collections/i })).toBeInTheDocument();
  });
});
