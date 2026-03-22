import { render, screen, waitFor } from '@testing-library/react';
import { useRouter, useParams } from 'next/navigation';
import EditRecipePage from './page';
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

jest.mock('@/components/RecipeForm', () => {
  return function MockRecipeForm({ 
    initialData, 
    onSubmit, 
    submitLabel 
  }: { 
    initialData?: any; 
    onSubmit: (data: any) => Promise<void>; 
    submitLabel?: string;
  }) {
    return (
      <div data-testid="recipe-form">
        <p>Form with initial data: {initialData?.title}</p>
        <p>Submit label: {submitLabel}</p>
        <button onClick={() => onSubmit({ title: 'Updated Recipe' })}>
          Submit
        </button>
      </div>
    );
  };
});

describe('EditRecipePage', () => {
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

    render(<EditRecipePage />);

    expect(mockPush).toHaveBeenCalledWith('/');
  });

  it('fetches and pre-populates form with existing recipe data', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue(mockRecipe);

    render(<EditRecipePage />);

    await waitFor(() => {
      expect(screen.getByText(/Form with initial data: Pasta Carbonara/)).toBeInTheDocument();
      expect(screen.getByText('Submit label: Update Recipe')).toBeInTheDocument();
    });

    expect(apiClient).toHaveBeenCalledWith('/api/recipes/1');
  });

  it('displays loading state while fetching recipe', () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockRecipe), 1000))
    );

    render(<EditRecipePage />);

    expect(screen.getByText('Loading recipe...')).toBeInTheDocument();
  });

  it('displays error message when recipe fetch fails', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockRejectedValue(new Error('Failed to load recipe'));

    render(<EditRecipePage />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load recipe')).toBeInTheDocument();
    });
  });

  it('displays error message when recipe not found', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue(null);

    render(<EditRecipePage />);

    await waitFor(() => {
      expect(screen.getByText('Recipe not found')).toBeInTheDocument();
    });
  });

  it('submits updated data to PUT endpoint and redirects on success', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    const updatedRecipe = { ...mockRecipe, title: 'Updated Recipe' };
    (apiClient as jest.Mock)
      .mockResolvedValueOnce(mockRecipe) // Initial fetch
      .mockResolvedValueOnce(updatedRecipe); // Update

    render(<EditRecipePage />);

    await waitFor(() => {
      expect(screen.getByText(/Form with initial data: Pasta Carbonara/)).toBeInTheDocument();
    });

    const submitButton = screen.getByText('Submit');
    submitButton.click();

    await waitFor(() => {
      expect(apiClient).toHaveBeenCalledWith('/api/recipes/1', {
        method: 'PUT',
        body: JSON.stringify({ title: 'Updated Recipe' }),
      });
      expect(mockPush).toHaveBeenCalledWith('/recipes/1');
    });
  });
});
