import { render, screen, fireEvent } from '@testing-library/react';
import MealTimeSlot from './MealTimeSlot';
import { MealPlan } from '@/types';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

// Mock MealPlanCard
jest.mock('./MealPlanCard', () => {
  return function MockMealPlanCard({ mealPlan, onDelete }: any) {
    return (
      <div data-testid={`meal-plan-${mealPlan.id}`}>
        {mealPlan.recipe?.title || 'Unknown Recipe'}
        <button onClick={() => onDelete(mealPlan.id)}>Delete</button>
      </div>
    );
  };
});

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

describe('MealTimeSlot', () => {
  const mockOnMealPlanUpdate = jest.fn();
  const mockOnMealPlanDelete = jest.fn();
  const mockOnRecipeDrop = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders meal time label', () => {
    render(
      <MealTimeSlot
        date="2024-01-15"
        mealTime="breakfast"
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    expect(screen.getByText('Breakfast')).toBeInTheDocument();
  });

  test('renders empty state when no meal plans', () => {
    render(
      <MealTimeSlot
        date="2024-01-15"
        mealTime="lunch"
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    expect(screen.getByText('Drag recipe here')).toBeInTheDocument();
  });

  test('renders meal plans when provided', () => {
    render(
      <MealTimeSlot
        date="2024-01-15"
        mealTime="breakfast"
        mealPlans={[mockMealPlan]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    expect(screen.getByTestId('meal-plan-1')).toBeInTheDocument();
    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
  });

  test('handles drag over event', () => {
    const { container } = render(
      <MealTimeSlot
        date="2024-01-15"
        mealTime="dinner"
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const slot = container.firstChild as HTMLElement;
    fireEvent.dragOver(slot);
    
    expect(screen.getByText('Drop here')).toBeInTheDocument();
  });

  test('handles drop event for new recipe', () => {
    const { container } = render(
      <MealTimeSlot
        date="2024-01-15"
        mealTime="lunch"
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const slot = container.firstChild as HTMLElement;
    
    const dropData = JSON.stringify({
      type: 'recipe',
      recipeId: 5,
    });
    
    fireEvent.drop(slot, {
      dataTransfer: {
        getData: () => dropData,
      },
    });
    
    expect(mockOnRecipeDrop).toHaveBeenCalledWith(5, '2024-01-15', 'lunch');
  });

  test('handles drop event for existing meal plan', () => {
    const { container } = render(
      <MealTimeSlot
        date="2024-01-16"
        mealTime="dinner"
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const slot = container.firstChild as HTMLElement;
    
    const dropData = JSON.stringify({
      type: 'meal-plan',
      mealPlanId: 10,
      recipeId: 5,
    });
    
    fireEvent.drop(slot, {
      dataTransfer: {
        getData: () => dropData,
      },
    });
    
    expect(mockOnMealPlanUpdate).toHaveBeenCalledWith(10, '2024-01-16', 'dinner');
  });

  test('handles drag leave event', () => {
    const { container } = render(
      <MealTimeSlot
        date="2024-01-15"
        mealTime="snack"
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const slot = container.firstChild as HTMLElement;
    
    fireEvent.dragOver(slot);
    expect(screen.getByText('Drop here')).toBeInTheDocument();
    
    fireEvent.dragLeave(slot);
    expect(screen.getByText('Drag recipe here')).toBeInTheDocument();
  });

  test('renders multiple meal plans', () => {
    const mealPlan2 = { ...mockMealPlan, id: 2, recipe: { ...mockMealPlan.recipe!, id: 2, title: 'Recipe 2' } };
    
    render(
      <MealTimeSlot
        date="2024-01-15"
        mealTime="breakfast"
        mealPlans={[mockMealPlan, mealPlan2]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    expect(screen.getByTestId('meal-plan-1')).toBeInTheDocument();
    expect(screen.getByTestId('meal-plan-2')).toBeInTheDocument();
  });
});
