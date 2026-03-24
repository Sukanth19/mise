import { render, screen, fireEvent } from '@testing-library/react';
import TemplateList from './TemplateList';
import { MealPlanTemplate } from '@/types';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

const mockTemplate: MealPlanTemplate = {
  id: 1,
  user_id: 1,
  name: 'Weekly Plan',
  description: 'My weekly meal plan',
  items: [
    {
      id: 1,
      template_id: 1,
      recipe_id: 1,
      recipe: {
        id: 1,
        user_id: 1,
        title: 'Breakfast Recipe',
        ingredients: [],
        steps: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      day_offset: 0,
      meal_time: 'breakfast',
    },
    {
      id: 2,
      template_id: 1,
      recipe_id: 2,
      recipe: {
        id: 2,
        user_id: 1,
        title: 'Lunch Recipe',
        ingredients: [],
        steps: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      day_offset: 0,
      meal_time: 'lunch',
    },
  ],
  created_at: '2024-01-01T00:00:00Z',
};

describe('TemplateList', () => {
  const mockOnApply = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders empty state when no templates', () => {
    render(
      <TemplateList
        templates={[]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('No templates yet')).toBeInTheDocument();
    expect(screen.getByText('Create a template to quickly apply meal plans')).toBeInTheDocument();
  });

  test('renders template name and description', () => {
    render(
      <TemplateList
        templates={[mockTemplate]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('Weekly Plan')).toBeInTheDocument();
    expect(screen.getByText('My weekly meal plan')).toBeInTheDocument();
  });

  test('renders recipe count', () => {
    render(
      <TemplateList
        templates={[mockTemplate]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('2 RECIPES')).toBeInTheDocument();
  });

  test('renders day count', () => {
    render(
      <TemplateList
        templates={[mockTemplate]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('1 DAYS')).toBeInTheDocument();
  });

  test('renders template item preview', () => {
    render(
      <TemplateList
        templates={[mockTemplate]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText(/Breakfast Recipe/)).toBeInTheDocument();
    expect(screen.getByText(/Lunch Recipe/)).toBeInTheDocument();
  });

  test('shows "more" indicator when more than 3 items', () => {
    const templateWithManyItems = {
      ...mockTemplate,
      items: [
        ...mockTemplate.items,
        { ...mockTemplate.items[0], id: 3 },
        { ...mockTemplate.items[0], id: 4 },
      ],
    };
    
    render(
      <TemplateList
        templates={[templateWithManyItems]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('+ 1 more...')).toBeInTheDocument();
  });

  test('calls onApply when apply button is clicked', () => {
    render(
      <TemplateList
        templates={[mockTemplate]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    const applyButton = screen.getByLabelText('Apply Weekly Plan');
    fireEvent.click(applyButton);
    
    expect(mockOnApply).toHaveBeenCalledWith(1);
  });

  test('calls onDelete when delete button is clicked', () => {
    render(
      <TemplateList
        templates={[mockTemplate]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    const deleteButton = screen.getByLabelText('Delete Weekly Plan');
    fireEvent.click(deleteButton);
    
    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });

  test('renders multiple templates', () => {
    const template2 = { ...mockTemplate, id: 2, name: 'Weekend Plan' };
    
    render(
      <TemplateList
        templates={[mockTemplate, template2]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('Weekly Plan')).toBeInTheDocument();
    expect(screen.getByText('Weekend Plan')).toBeInTheDocument();
  });

  test('handles template without description', () => {
    const templateNoDesc = { ...mockTemplate, description: undefined };
    
    render(
      <TemplateList
        templates={[templateNoDesc]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('Weekly Plan')).toBeInTheDocument();
    expect(screen.queryByText('My weekly meal plan')).not.toBeInTheDocument();
  });

  test('displays singular "RECIPE" for single item', () => {
    const templateOneItem = {
      ...mockTemplate,
      items: [mockTemplate.items[0]],
    };
    
    render(
      <TemplateList
        templates={[templateOneItem]}
        onApply={mockOnApply}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('1 RECIPE')).toBeInTheDocument();
  });
});
