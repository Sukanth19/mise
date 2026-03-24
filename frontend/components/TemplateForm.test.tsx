import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TemplateForm from './TemplateForm';
import { Recipe } from '@/types';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

// Mock API client
jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
}));

import { apiClient } from '@/lib/api';

const mockRecipes: Recipe[] = [
  {
    id: 1,
    user_id: 1,
    title: 'Recipe 1',
    ingredients: [],
    steps: [],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    user_id: 1,
    title: 'Recipe 2',
    ingredients: [],
    steps: [],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

describe('TemplateForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (apiClient as jest.Mock).mockResolvedValue({ recipes: mockRecipes });
  });

  test('renders form fields', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByLabelText(/Template Name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
    });
  });

  test('loads recipes on mount', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(apiClient).toHaveBeenCalledWith('/api/recipes');
    });
  });

  test('shows loading state initially', () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    expect(screen.getByText('Loading recipes...')).toBeInTheDocument();
  });

  test('adds new template item', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('ADD RECIPE')).toBeInTheDocument();
    });
    
    const addButton = screen.getByText('ADD RECIPE');
    fireEvent.click(addButton);
    
    expect(screen.getByLabelText(/Recipe/)).toBeInTheDocument();
  });

  test('removes template item', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('ADD RECIPE')).toBeInTheDocument();
    });
    
    const addButton = screen.getByText('ADD RECIPE');
    fireEvent.click(addButton);
    
    const removeButton = screen.getByLabelText('Remove recipe');
    fireEvent.click(removeButton);
    
    expect(screen.queryByLabelText(/Recipe/)).not.toBeInTheDocument();
  });

  test('validates template name is required', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('CREATE TEMPLATE')).toBeInTheDocument();
    });
    
    const submitButton = screen.getByText('CREATE TEMPLATE');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Template name is required')).toBeInTheDocument();
    });
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('validates at least one recipe is required', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('CREATE TEMPLATE')).toBeInTheDocument();
    });
    
    const nameInput = screen.getByLabelText(/Template Name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Template' } });
    
    const submitButton = screen.getByText('CREATE TEMPLATE');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Add at least one recipe to the template')).toBeInTheDocument();
    });
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('submits valid template', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('ADD RECIPE')).toBeInTheDocument();
    });
    
    // Fill in name
    const nameInput = screen.getByLabelText(/Template Name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Template' } });
    
    // Add a recipe
    const addButton = screen.getByText('ADD RECIPE');
    fireEvent.click(addButton);
    
    // Submit
    const submitButton = screen.getByText('CREATE TEMPLATE');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'Test Template',
        items: [
          {
            recipe_id: 1,
            day_offset: 0,
            meal_time: 'breakfast',
          },
        ],
      });
    });
  });

  test('calls onCancel when cancel button is clicked', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('CANCEL')).toBeInTheDocument();
    });
    
    const cancelButton = screen.getByText('CANCEL');
    fireEvent.click(cancelButton);
    
    expect(mockOnCancel).toHaveBeenCalled();
  });

  test('updates recipe selection', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('ADD RECIPE')).toBeInTheDocument();
    });
    
    const addButton = screen.getByText('ADD RECIPE');
    fireEvent.click(addButton);
    
    const recipeSelect = screen.getByLabelText(/Recipe/);
    fireEvent.change(recipeSelect, { target: { value: '2' } });
    
    expect(recipeSelect).toHaveValue('2');
  });

  test('updates day offset', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('ADD RECIPE')).toBeInTheDocument();
    });
    
    const addButton = screen.getByText('ADD RECIPE');
    fireEvent.click(addButton);
    
    const dayInput = screen.getByLabelText(/Day/);
    fireEvent.change(dayInput, { target: { value: '3' } });
    
    expect(dayInput).toHaveValue(3);
  });

  test('updates meal time', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('ADD RECIPE')).toBeInTheDocument();
    });
    
    const addButton = screen.getByText('ADD RECIPE');
    fireEvent.click(addButton);
    
    const mealTimeSelect = screen.getByLabelText(/Meal Time/);
    fireEvent.change(mealTimeSelect, { target: { value: 'dinner' } });
    
    expect(mealTimeSelect).toHaveValue('dinner');
  });

  test('includes description in submission when provided', async () => {
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('ADD RECIPE')).toBeInTheDocument();
    });
    
    const nameInput = screen.getByLabelText(/Template Name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Template' } });
    
    const descInput = screen.getByLabelText(/Description/i);
    fireEvent.change(descInput, { target: { value: 'Test description' } });
    
    const addButton = screen.getByText('ADD RECIPE');
    fireEvent.click(addButton);
    
    const submitButton = screen.getByText('CREATE TEMPLATE');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'Test Template',
        description: 'Test description',
        items: expect.any(Array),
      });
    });
  });

  test('handles API error when loading recipes', async () => {
    (apiClient as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    render(<TemplateForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load recipes')).toBeInTheDocument();
    });
  });
});
