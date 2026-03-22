import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useRouter, useParams } from 'next/navigation';
import RecipeDetailPage from './page';
import { apiClient, getToken } from '@/lib/api';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}));

jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
  getToken: jest.fn(),
}));

jest.mock('@/components/RecipeDetail', () => {
  return function MockRecipeDetail({ recipe }: { recipe: any }) {
    return (
      <div data-testid="recipe-detail">
        <h1>{recipe.title}</h1>
        <p>{recipe.ingredients.join(', ')}</p>
      </div>
    );
  };
});

jest.mock('@/components/DeleteConfirmationModal', () => {
  return function MockDeleteConfirmationModal({
    isOpen,
    onClose,
    onConfirm,
    title,
    isDeleting,
  }: {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    isDeleting?: boolean;
  }) {
    if (!isOpen) return null;
    return (
      <div data-testid="delete-modal">
        <p>Delete "{title}"?</p>
        <button onClick={onClose}>Cancel</button>
        <button onClick={onConfirm} disabled={isDeleting}>
          {isDeleting ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    );
  };
});

describe('RecipeDetailPage', () => {
  const mockPush = jest.fn();
  const mockRecipe = {
    id: 1,
    user_id: 1,
    title: 'Pasta Carbonara',
    image_url: 'https://example.com/pasta.jpg',
    ingredients: ['pasta', 'eggs', 'bacon', 'parmesan'],
    steps: ['Cook pasta', 'Mix eggs with cheese', 'Combine with bacon'],
    tags: ['italian', 'dinner'],
    reference_link: 'https://example.com/recipe',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (useParams as jest.Mock).mockReturnValue({ id: '1' });
  });

  it('redirects to login if not authenticated', () => {
    (getToken as jest.Mock).mockReturnValue(null);

    render(<RecipeDetailPage />);

    expect(mockPush).toHaveBeenCalledWith('/');
  });

  it('fetches and displays recipe details', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue(mockRecipe);

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
      expect(screen.getByText(/pasta, eggs, bacon, parmesan/)).toBeInTheDocument();
    });

    expect(apiClient).toHaveBeenCalledWith('/api/recipes/1');
  });

  it('displays loading state while fetching', () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockRecipe), 1000))
    );

    render(<RecipeDetailPage />);

    expect(screen.getByText('Loading recipe...')).toBeInTheDocument();
  });

  it('displays 404 error when recipe not found', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockRejectedValue(new Error('HTTP 404'));

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Recipe Not Found')).toBeInTheDocument();
      expect(screen.getByText('Recipe not found')).toBeInTheDocument();
    });
  });

  it('displays generic error message on fetch failure', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('navigates to edit page when Edit button is clicked', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue(mockRecipe);

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    const editButton = screen.getByText('Edit Recipe');
    fireEvent.click(editButton);

    expect(mockPush).toHaveBeenCalledWith('/recipes/1/edit');
  });

  it('navigates back to dashboard when Back button is clicked', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue(mockRecipe);

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    const backButton = screen.getByText('Back to Dashboard');
    fireEvent.click(backButton);

    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('does not delete recipe when confirmation is cancelled', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue(mockRecipe);

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    // Click delete button to open modal
    const deleteButton = screen.getByText('Delete Recipe');
    fireEvent.click(deleteButton);

    // Modal should be visible
    await waitFor(() => {
      expect(screen.getByTestId('delete-modal')).toBeInTheDocument();
    });

    // Click cancel button
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    // Modal should close and no delete API call should be made
    await waitFor(() => {
      expect(screen.queryByTestId('delete-modal')).not.toBeInTheDocument();
    });
    expect(apiClient).toHaveBeenCalledTimes(1); // Only the initial fetch
  });

  it('deletes recipe and redirects to dashboard when confirmed', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock)
      .mockResolvedValueOnce(mockRecipe) // Initial fetch
      .mockResolvedValueOnce({ message: 'Recipe deleted successfully' }); // Delete

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    // Click delete button to open modal
    const deleteButton = screen.getByText('Delete Recipe');
    fireEvent.click(deleteButton);

    // Modal should be visible
    await waitFor(() => {
      expect(screen.getByTestId('delete-modal')).toBeInTheDocument();
    });

    // Click confirm button in modal
    const confirmButton = screen.getByText('Delete');
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(apiClient).toHaveBeenCalledWith('/api/recipes/1', {
        method: 'DELETE',
      });
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('displays alert on delete failure', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock)
      .mockResolvedValueOnce(mockRecipe)
      .mockRejectedValueOnce(new Error('Delete failed'));
    
    // Mock window.alert
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});

    render(<RecipeDetailPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    // Click delete button to open modal
    const deleteButton = screen.getByText('Delete Recipe');
    fireEvent.click(deleteButton);

    // Modal should be visible
    await waitFor(() => {
      expect(screen.getByTestId('delete-modal')).toBeInTheDocument();
    });

    // Click confirm button in modal
    const confirmButton = screen.getByText('Delete');
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(alertMock).toHaveBeenCalledWith('Delete failed');
    });

    alertMock.mockRestore();
  });
});
