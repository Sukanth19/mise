import { render, screen, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import NewRecipePage from './page';
import { getToken, apiClient } from '@/lib/api';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/lib/api', () => ({
  getToken: jest.fn(),
  apiClient: jest.fn(),
}));

jest.mock('@/components/RecipeForm', () => {
  return function MockRecipeForm({ onSubmit, submitLabel }: any) {
    return (
      <div data-testid="recipe-form">
        <span>Submit Label: {submitLabel}</span>
        <button
          data-testid="submit-button"
          onClick={() => onSubmit({
            title: 'Test Recipe',
            ingredients: ['ingredient 1'],
            steps: ['step 1'],
          })}
        >
          Submit
        </button>
      </div>
    );
  };
});

describe('NewRecipePage', () => {
  const mockPush = jest.fn();
  const mockRouter = { push: mockPush };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  it('redirects to login if not authenticated', () => {
    (getToken as jest.Mock).mockReturnValue(null);

    render(<NewRecipePage />);

    expect(mockPush).toHaveBeenCalledWith('/');
  });

  it('renders the page with RecipeForm when authenticated', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');

    render(<NewRecipePage />);

    await waitFor(() => {
      expect(screen.getByText('Create New Recipe')).toBeInTheDocument();
    });

    expect(screen.getByText('Add a new recipe to your collection')).toBeInTheDocument();
    expect(screen.getByTestId('recipe-form')).toBeInTheDocument();
    expect(screen.getByText('Submit Label: Create Recipe')).toBeInTheDocument();
  });

  it('renders back button', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');

    render(<NewRecipePage />);

    await waitFor(() => {
      expect(screen.getByText('Back to Dashboard')).toBeInTheDocument();
    });
  });

  it('renders the page correctly when authenticated', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');

    render(<NewRecipePage />);

    await waitFor(() => {
      expect(screen.getByText('Create New Recipe')).toBeInTheDocument();
      expect(screen.getByText('Add a new recipe to your collection')).toBeInTheDocument();
      expect(screen.getByTestId('recipe-form')).toBeInTheDocument();
      expect(screen.getByText('Submit Label: Create Recipe')).toBeInTheDocument();
    });
  });

  it('submits recipe and redirects to detail page on success', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue({ id: 123 });

    render(<NewRecipePage />);

    await waitFor(() => {
      expect(screen.getByTestId('submit-button')).toBeInTheDocument();
    });

    const submitButton = screen.getByTestId('submit-button');
    submitButton.click();

    await waitFor(() => {
      expect(apiClient).toHaveBeenCalledWith('/api/recipes', {
        method: 'POST',
        body: JSON.stringify({
          title: 'Test Recipe',
          ingredients: ['ingredient 1'],
          steps: ['step 1'],
        }),
      });
      expect(mockPush).toHaveBeenCalledWith('/recipes/123');
    });
  });
});
