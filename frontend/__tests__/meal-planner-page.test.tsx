import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import MealPlannerPage from '@/app/meal-planner/page';
import { apiClient, getToken } from '@/lib/api';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
  getToken: jest.fn(),
}));

const mockRouter = {
  push: jest.fn(),
};

const mockMealPlans = [
  {
    id: 1,
    user_id: 1,
    recipe_id: 1,
    recipe: {
      id: 1,
      user_id: 1,
      title: 'Test Recipe 1',
      image_url: '/images/test1.jpg',
      ingredients: ['ingredient 1'],
      steps: ['step 1'],
      tags: ['tag1'],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    meal_date: '2024-01-15',
    meal_time: 'breakfast' as const,
    created_at: '2024-01-01T00:00:00Z',
  },
];

const mockRecipes = [
  {
    id: 1,
    user_id: 1,
    title: 'Test Recipe 1',
    image_url: '/images/test1.jpg',
    ingredients: ['ingredient 1'],
    steps: ['step 1'],
    tags: ['tag1'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    user_id: 1,
    title: 'Test Recipe 2',
    image_url: '/images/test2.jpg',
    ingredients: ['ingredient 2'],
    steps: ['step 2'],
    tags: ['tag2'],
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
];

const mockTemplates = [
  {
    id: 1,
    user_id: 1,
    name: 'Weekly Plan',
    description: 'My weekly meal plan',
    items: [
      {
        id: 1,
        template_id: 1,
        recipe_id: 1,
        recipe: mockRecipes[0],
        day_offset: 0,
        meal_time: 'breakfast' as const,
      },
    ],
    created_at: '2024-01-01T00:00:00Z',
  },
];

describe('MealPlannerPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (getToken as jest.Mock).mockReturnValue('mock-token');
  });

  it('redirects to login if not authenticated', () => {
    (getToken as jest.Mock).mockReturnValue(null);
    render(<MealPlannerPage />);
    expect(mockRouter.push).toHaveBeenCalledWith('/');
  });

  it('renders loading state initially', () => {
    (apiClient as jest.Mock).mockImplementation(() => new Promise(() => {}));
    render(<MealPlannerPage />);
    expect(screen.getByText(/loading meal planner/i)).toBeInTheDocument();
  });

  it('fetches and displays meal plans, recipes, and templates', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: mockMealPlans })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: mockTemplates });

    render(<MealPlannerPage />);

    await waitFor(() => {
      expect(screen.getByText('MEAL PLANNER')).toBeInTheDocument();
    });

    // Check that API was called with correct endpoints
    expect(apiClient).toHaveBeenCalledWith(expect.stringContaining('/api/meal-plans?start_date='));
    expect(apiClient).toHaveBeenCalledWith('/api/recipes');
    expect(apiClient).toHaveBeenCalledWith('/api/meal-plan-templates');
  });

  it('displays empty state when no meal plans exist', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: [] })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: [] });

    render(<MealPlannerPage />);

    await waitFor(() => {
      expect(screen.getByText(/NO MEAL PLANS YET/i)).toBeInTheDocument();
    });
  });

  it('displays recipe sidebar with search functionality', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: mockMealPlans })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: [] });

    render(<MealPlannerPage />);

    await waitFor(() => {
      expect(screen.getByText('RECIPES')).toBeInTheDocument();
    });

    // Check recipes are displayed
    expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
    expect(screen.getByText('Test Recipe 2')).toBeInTheDocument();

    // Test search
    const searchInput = screen.getByPlaceholderText(/search recipes/i);
    fireEvent.change(searchInput, { target: { value: 'Recipe 1' } });

    await waitFor(() => {
      expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
      expect(screen.queryByText('Test Recipe 2')).not.toBeInTheDocument();
    });
  });

  it('toggles sidebar visibility', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: mockMealPlans })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: [] });

    render(<MealPlannerPage />);

    await waitFor(() => {
      expect(screen.getByText('RECIPES')).toBeInTheDocument();
    });

    // Click hide button
    const hideButton = screen.getByText(/HIDE RECIPES/i);
    fireEvent.click(hideButton);

    await waitFor(() => {
      expect(screen.queryByText('RECIPES')).not.toBeInTheDocument();
    });

    // Click show button
    const showButton = screen.getByText(/SHOW RECIPES/i);
    fireEvent.click(showButton);

    await waitFor(() => {
      expect(screen.getByText('RECIPES')).toBeInTheDocument();
    });
  });

  it('shows template form when create template button is clicked', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: mockMealPlans })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: [] });

    render(<MealPlannerPage />);

    await waitFor(() => {
      expect(screen.getByText('MEAL PLANNER')).toBeInTheDocument();
    });

    const createTemplateButton = screen.getByText(/CREATE TEMPLATE/i);
    fireEvent.click(createTemplateButton);

    await waitFor(() => {
      expect(screen.getByText(/Create Meal Plan Template/i)).toBeInTheDocument();
    });
  });

  it('shows template list when templates button is clicked', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: mockMealPlans })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: mockTemplates });

    render(<MealPlannerPage />);

    await waitFor(() => {
      expect(screen.getByText('MEAL PLANNER')).toBeInTheDocument();
    });

    const templatesButton = screen.getByText(/TEMPLATES/i);
    fireEvent.click(templatesButton);

    await waitFor(() => {
      expect(screen.getByText('MY TEMPLATES')).toBeInTheDocument();
      expect(screen.getByText('Weekly Plan')).toBeInTheDocument();
    });
  });

  it('handles error state', async () => {
    (apiClient as jest.Mock).mockRejectedValue(new Error('Failed to load data'));

    render(<MealPlannerPage />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load data/i)).toBeInTheDocument();
    });
  });

  it('disables export button when no meal plans exist', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: [] })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: [] });

    render(<MealPlannerPage />);

    await waitFor(() => {
      const exportButton = screen.getByText(/EXPORT ICAL/i).closest('button');
      expect(exportButton).toBeDisabled();
    });
  });

  it('enables export button when meal plans exist', async () => {
    (apiClient as jest.Mock)
      .mockResolvedValueOnce({ meal_plans: mockMealPlans })
      .mockResolvedValueOnce({ recipes: mockRecipes })
      .mockResolvedValueOnce({ templates: [] });

    render(<MealPlannerPage />);

    await waitFor(() => {
      const exportButton = screen.getByText(/EXPORT ICAL/i).closest('button');
      expect(exportButton).not.toBeDisabled();
    });
  });
});
