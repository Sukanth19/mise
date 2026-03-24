import { render, screen, fireEvent } from '@testing-library/react';
import MealPlannerCalendar from './MealPlannerCalendar';
import { MealPlan } from '@/types';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

// Mock MealTimeSlot
jest.mock('./MealTimeSlot', () => {
  return function MockMealTimeSlot({ date, mealTime, mealPlans }: any) {
    return (
      <div data-testid={`meal-time-slot-${date}-${mealTime}`}>
        {mealTime} - {mealPlans.length} meals
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
    ingredients: ['ingredient 1'],
    steps: ['step 1'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  meal_date: '2024-01-15',
  meal_time: 'breakfast',
  created_at: '2024-01-01T00:00:00Z',
};

describe('MealPlannerCalendar', () => {
  const mockOnMealPlanUpdate = jest.fn();
  const mockOnMealPlanDelete = jest.fn();
  const mockOnRecipeDrop = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders calendar with navigation buttons', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    expect(screen.getByLabelText('Previous period')).toBeInTheDocument();
    expect(screen.getByText('TODAY')).toBeInTheDocument();
    expect(screen.getByLabelText('Next period')).toBeInTheDocument();
  });

  test('renders view mode toggle buttons', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    expect(screen.getByText('WEEK')).toBeInTheDocument();
    expect(screen.getByText('MONTH')).toBeInTheDocument();
  });

  test('switches to month view when month button clicked', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const monthButton = screen.getByText('MONTH');
    fireEvent.click(monthButton);
    
    // In month view, we should see day headers
    expect(screen.getByText('Sun')).toBeInTheDocument();
    expect(screen.getByText('Mon')).toBeInTheDocument();
    expect(screen.getByText('Tue')).toBeInTheDocument();
  });

  test('navigates to previous week', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const prevButton = screen.getByLabelText('Previous period');
    fireEvent.click(prevButton);
    
    // Calendar should still be rendered
    expect(screen.getByText('TODAY')).toBeInTheDocument();
  });

  test('navigates to next week', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const nextButton = screen.getByLabelText('Next period');
    fireEvent.click(nextButton);
    
    // Calendar should still be rendered
    expect(screen.getByText('TODAY')).toBeInTheDocument();
  });

  test('returns to today when today button clicked', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    // Navigate away
    const nextButton = screen.getByLabelText('Next period');
    fireEvent.click(nextButton);
    
    // Return to today
    const todayButton = screen.getByText('TODAY');
    fireEvent.click(todayButton);
    
    // Should show current date
    expect(screen.getByText('TODAY')).toBeInTheDocument();
  });

  test('renders meal time slots in week view', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[mockMealPlan]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    // Week view should show meal time slots
    const slots = screen.getAllByTestId(/meal-time-slot-/);
    expect(slots.length).toBeGreaterThan(0);
  });

  test('displays current date range in header', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    // Should display a date range (format varies by locale)
    const header = screen.getByRole('heading', { level: 2 });
    expect(header).toBeInTheDocument();
    expect(header.textContent).toMatch(/\d+/); // Should contain numbers (dates)
  });

  test('week view is active by default', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const weekButton = screen.getByText('WEEK');
    expect(weekButton.className).toContain('bg-primary');
  });

  test('month view button becomes active when clicked', () => {
    render(
      <MealPlannerCalendar
        mealPlans={[]}
        onMealPlanUpdate={mockOnMealPlanUpdate}
        onMealPlanDelete={mockOnMealPlanDelete}
        onRecipeDrop={mockOnRecipeDrop}
      />
    );
    
    const monthButton = screen.getByText('MONTH');
    fireEvent.click(monthButton);
    
    expect(monthButton.className).toContain('bg-primary');
  });
});
