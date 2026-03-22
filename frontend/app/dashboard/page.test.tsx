import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import DashboardPage from './page';
import { apiClient, getToken } from '@/lib/api';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
  getToken: jest.fn(),
}));

jest.mock('@/components/RecipeGrid', () => {
  return function MockRecipeGrid({ recipes }: { recipes: any[] }) {
    return (
      <div data-testid="recipe-grid">
        {recipes.map((recipe) => (
          <div key={recipe.id} data-testid={`recipe-${recipe.id}`}>
            {recipe.title}
          </div>
        ))}
      </div>
    );
  };
});

jest.mock('@/components/SearchBar', () => {
  return function MockSearchBar({ onSearch }: { onSearch: (query: string) => void }) {
    return (
      <input
        data-testid="search-bar"
        onChange={(e) => onSearch(e.target.value)}
        placeholder="Search recipes..."
      />
    );
  };
});

describe('DashboardPage', () => {
  const mockPush = jest.fn();
  const mockRecipes = [
    {
      id: 1,
      user_id: 1,
      title: 'Pasta Carbonara',
      image_url: 'https://example.com/pasta.jpg',
      ingredients: ['pasta', 'eggs', 'bacon'],
      steps: ['Cook pasta', 'Mix eggs', 'Combine'],
      tags: ['italian', 'dinner'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      user_id: 1,
      title: 'Chocolate Cake',
      image_url: 'https://example.com/cake.jpg',
      ingredients: ['flour', 'sugar', 'cocoa'],
      steps: ['Mix ingredients', 'Bake'],
      tags: ['dessert'],
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
  });

  it('redirects to login if not authenticated', () => {
    (getToken as jest.Mock).mockReturnValue(null);

    render(<DashboardPage />);

    expect(mockPush).toHaveBeenCalledWith('/');
  });

  it('fetches and displays recipes', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue({ recipes: mockRecipes });

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
      expect(screen.getByText('Chocolate Cake')).toBeInTheDocument();
    });

    expect(apiClient).toHaveBeenCalledWith('/api/recipes');
  });

  it('displays empty state when no recipes exist', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue({ recipes: [] });

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('No recipes yet')).toBeInTheDocument();
      expect(screen.getByText('Start building your recipe collection!')).toBeInTheDocument();
    });
  });

  it('displays loading state while fetching', () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ recipes: [] }), 1000))
    );

    render(<DashboardPage />);

    expect(screen.getByText('Loading recipes...')).toBeInTheDocument();
  });

  it('displays error message on fetch failure', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('navigates to create recipe page when Create Recipe button is clicked', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockResolvedValue({ recipes: mockRecipes });

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    const createButton = screen.getAllByText('Create Recipe')[0];
    fireEvent.click(createButton);

    expect(mockPush).toHaveBeenCalledWith('/recipes/new');
  });

  it('performs search when search query is entered', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ recipes: [mockRecipes[0]] });

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    const searchBar = screen.getByTestId('search-bar');
    fireEvent.change(searchBar, { target: { value: 'pasta' } });

    await waitFor(() => {
      expect(apiClient).toHaveBeenCalledWith('/api/recipes?search=pasta');
    });
  });

  it('displays search results empty state when no matches found', async () => {
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ recipes: [] });

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
    });

    const searchBar = screen.getByTestId('search-bar');
    fireEvent.change(searchBar, { target: { value: 'pizza' } });

    await waitFor(() => {
      expect(screen.getByText(/No recipes found matching "pizza"/)).toBeInTheDocument();
    });
  });
});
