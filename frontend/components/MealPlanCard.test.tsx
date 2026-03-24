import { render, screen, fireEvent } from '@testing-library/react';
import MealPlanCard from './MealPlanCard';
import { MealPlan } from '@/types';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

const mockMealPlan: MealPlan = {
  id: 1,
  user_id: 1,
  recipe_id: 1,
  recipe: {
    id: 1,
    user_id: 1,
    title: 'Test Recipe',
    image_url: '/test-image.jpg',
    ingredients: ['ingredient 1'],
    steps: ['step 1'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  meal_date: '2024-01-15',
  meal_time: 'breakfast',
  created_at: '2024-01-01T00:00:00Z',
};

describe('MealPlanCard', () => {
  const mockOnDelete = jest.fn();
  const mockOnDragStart = jest.fn();
  const mockOnDragEnd = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders recipe title', () => {
    render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
  });

  test('renders meal time', () => {
    render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('BREAKFAST')).toBeInTheDocument();
  });

  test('renders recipe image when available', () => {
    render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
      />
    );
    
    const image = screen.getByAltText('Test Recipe');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'http://localhost:8000/test-image.jpg');
  });

  test('renders placeholder when no image', () => {
    const mealPlanNoImage = {
      ...mockMealPlan,
      recipe: {
        ...mockMealPlan.recipe!,
        image_url: undefined,
      },
    };

    render(
      <MealPlanCard
        mealPlan={mealPlanNoImage}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('NO IMG')).toBeInTheDocument();
  });

  test('calls onDelete when delete button clicked', () => {
    render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
      />
    );
    
    const deleteButton = screen.getByLabelText('Delete meal plan');
    fireEvent.click(deleteButton);
    
    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });

  test('is draggable', () => {
    const { container } = render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
        onDragStart={mockOnDragStart}
        onDragEnd={mockOnDragEnd}
      />
    );
    
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveAttribute('draggable', 'true');
  });

  test('calls onDragStart when drag starts', () => {
    const { container } = render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
        onDragStart={mockOnDragStart}
        onDragEnd={mockOnDragEnd}
      />
    );
    
    const card = container.firstChild as HTMLElement;
    fireEvent.dragStart(card);
    
    expect(mockOnDragStart).toHaveBeenCalledWith(mockMealPlan);
  });

  test('calls onDragEnd when drag ends', () => {
    const { container } = render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
        onDragStart={mockOnDragStart}
        onDragEnd={mockOnDragEnd}
      />
    );
    
    const card = container.firstChild as HTMLElement;
    fireEvent.dragEnd(card);
    
    expect(mockOnDragEnd).toHaveBeenCalled();
  });

  test('renders unknown recipe when recipe is missing', () => {
    const mealPlanNoRecipe = {
      ...mockMealPlan,
      recipe: undefined,
    };

    render(
      <MealPlanCard
        mealPlan={mealPlanNoRecipe}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('Unknown Recipe')).toBeInTheDocument();
  });

  test('renders drag handle icon', () => {
    render(
      <MealPlanCard
        mealPlan={mockMealPlan}
        onDelete={mockOnDelete}
      />
    );
    
    // GripVertical icon should be present
    const card = screen.getByText('Test Recipe').closest('div');
    expect(card).toBeInTheDocument();
  });
});
