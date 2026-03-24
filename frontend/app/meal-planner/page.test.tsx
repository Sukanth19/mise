import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MealPlannerPage from './page';
import { apiClient, getToken } from '@/lib/api';

// Mock dependencies
jest.mock('@/lib/api');
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

jest.mock('@/components/MealPlannerCalendar', () => {
  return function MockMealPlannerCalendar({ mealPlans }: any) {
    return <div data-testid="meal-planner-calendar">Calendar with {mealPlans.length} meal plans</div>;
  };
});

jest.mock('@/components/TemplateForm', () => {
  return function MockTemplateForm({ onSubmit, onCancel }: any) {
    return (
      <div data-testid="template-form">
        <button onClick={() => onSubmit({ name: 'Test Template', items: [] })}>Submit</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    );
  };
});

jest.mock('@/components/TemplateList', () => {
  return function MockTemplateList({ templates, onApply, onDelete }: any) {
    return (
      <div data-testid="template-list">
        {templates.map((t: any) => (
          <div key={t.id}>
            {t.name}
            <button onClick={() => onApply(t.id)}>Apply</button>
            <button onClick={() => onDelete(t.id)}>Delete</button>
          </div>
        ))}
      </div>
    );
  };
});

const mockMealPlans = [
  {
    id: 1,
    user_id: 1,
    recipe_id: 1,
    recipe: {
      id: 1,
      user_id: 1,
      title: 'Test Recipe',
      ingredients: ['ingredient 1'],
      steps: ['step 1'],
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
    title: 'Test Recipe',
    ingredients: ['ingredient 1'],
    steps: ['step 1'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const mockTemplates = [
  {
    id: 1,
    user_id: 1,
    name: 'Test Template',
    items: [],
    created_at: '2024-01-01T00:00:00Z',
  },
];

describe('MealPlannerPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (getToken as jest.Mock).mockReturnValue('fake-token');
    (apiClient as jest.Mock).mockImplementation((endpoint: string) => {
      if (endpoint.includes('/api/meal-plans')) {
        return Promise.resolve({ meal_plans: mockMealPlans });
      }
      if (endpoint.includes('/api/recipes')) {
        return Promise.resolve({ recipes: mockRecipes });
      }
      if (endpoint.includes('/api/meal-plan-templates')) {
        return Promise.resolve({ templates: mockTemplates });
      }
      return Promise.resolve({});
    });
  });

  test('renders page title', async () => {
    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByText('MEAL PLANNER')).toBeInTheDocument();
    });
  });

  test('renders action buttons', async () => {
    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByText('EXPORT TO ICAL')).toBeInTheDocument();
      expect(screen.getByText('TEMPLATES')).toBeInTheDocument();
      expect(screen.getByText('CREATE TEMPLATE')).toBeInTheDocument();
    });
  });

  test('renders recipe sidebar', async () => {
    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByText('RECIPES')).toBeInTheDocument();
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });
  });

  test('renders calendar with meal plans', async () => {
    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('meal-planner-calendar')).toBeInTheDocument();
      expect(screen.getByText(/Calendar with 1 meal plans/)).toBeInTheDocument();
    });
  });

  test('shows empty state when no meal plans', async () => {
    (apiClient as jest.Mock).mockImplementation((endpoint: string) => {
      if (endpoint.includes('/api/meal-plans')) {
        return Promise.resolve({ meal_plans: [] });
      }
      if (endpoint.includes('/api/recipes')) {
        return Promise.resolve({ recipes: mockRecipes });
      }
      if (endpoint.includes('/api/meal-plan-templates')) {
        return Promise.resolve({ templates: [] });
      }
      return Promise.resolve({});
    });

    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByText('No meal plans yet')).toBeInTheDocument();
      expect(screen.getByText(/Drag recipes from the sidebar/)).toBeInTheDocument();
    });
  });

  test('shows template form when create template button clicked', async () => {
    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByText('CREATE TEMPLATE')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('CREATE TEMPLATE'));
    
    await waitFor(() => {
      expect(screen.getByTestId('template-form')).toBeInTheDocument();
    });
  });

  test('hides template form when cancel clicked', async () => {
    render(<MealPlannerPage />);
    
    await waitFor(() => {
      fireEvent.click(screen.getByText('CREATE TEMPLATE'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('template-form')).toBeInTheDocument();
    });

    fireEvent.click(screen.getAllByText('Cancel')[0]);
    
    await waitFor(() => {
      expect(screen.queryByTestId('template-form')).not.toBeInTheDocument();
    });
  });

  test('shows template list when templates button clicked', async () => {
    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByText('TEMPLATES')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('TEMPLATES'));
    
    await waitFor(() => {
      expect(screen.getByTestId('template-list')).toBeInTheDocument();
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });
  });

  test('export button is disabled when no meal plans', async () => {
    (apiClient as jest.Mock).mockImplementation((endpoint: string) => {
      if (endpoint.includes('/api/meal-plans')) {
        return Promise.resolve({ meal_plans: [] });
      }
      if (endpoint.includes('/api/recipes')) {
        return Promise.resolve({ recipes: mockRecipes });
      }
      if (endpoint.includes('/api/meal-plan-templates')) {
        return Promise.resolve({ templates: [] });
      }
      return Promise.resolve({});
    });

    render(<MealPlannerPage />);
    
    await waitFor(() => {
      const exportButton = screen.getByText('EXPORT TO ICAL').closest('button');
      expect(exportButton).toBeDisabled();
    });
  });

  test('shows empty state for recipes when no recipes available', async () => {
    (apiClient as jest.Mock).mockImplementation((endpoint: string) => {
      if (endpoint.includes('/api/meal-plans')) {
        return Promise.resolve({ meal_plans: [] });
      }
      if (endpoint.includes('/api/recipes')) {
        return Promise.resolve({ recipes: [] });
      }
      if (endpoint.includes('/api/meal-plan-templates')) {
        return Promise.resolve({ templates: [] });
      }
      return Promise.resolve({});
    });

    render(<MealPlannerPage />);
    
    await waitFor(() => {
      expect(screen.getByText('No recipes yet')).toBeInTheDocument();
      expect(screen.getByText('Create recipes to start planning meals')).toBeInTheDocument();
    });
  });
});
