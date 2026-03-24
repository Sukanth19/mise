import { render, screen } from '@testing-library/react';
import NutritionSummary from './NutritionSummary';

describe('NutritionSummary', () => {
  const mockDailyTotals = [
    {
      date: '2024-01-15',
      calories: 1800,
      protein_g: 90,
      carbs_g: 200,
      fat_g: 60,
      fiber_g: 25,
    },
    {
      date: '2024-01-16',
      calories: 2000,
      protein_g: 100,
      carbs_g: 220,
      fat_g: 70,
      fiber_g: 30,
    },
  ];

  const mockWeeklyTotal = {
    calories: 12600,
    protein_g: 630,
    carbs_g: 1400,
    fat_g: 420,
    fiber_g: 175,
  };

  it('displays weekly total nutrition', () => {
    render(
      <NutritionSummary 
        dailyTotals={mockDailyTotals} 
        weeklyTotal={mockWeeklyTotal}
        missingNutritionCount={0}
      />
    );

    expect(screen.getByText(/weekly total/i)).toBeInTheDocument();
    expect(screen.getByText('12600.0')).toBeInTheDocument();
    expect(screen.getByText('630.0')).toBeInTheDocument();
    expect(screen.getByText('1400.0')).toBeInTheDocument();
    expect(screen.getByText('420.0')).toBeInTheDocument();
    expect(screen.getByText('175.0')).toBeInTheDocument();
  });

  it('displays daily breakdown for each day', () => {
    render(
      <NutritionSummary 
        dailyTotals={mockDailyTotals} 
        weeklyTotal={mockWeeklyTotal}
        missingNutritionCount={0}
      />
    );

    expect(screen.getByText(/daily breakdown/i)).toBeInTheDocument();
    expect(screen.getByText('1800.0')).toBeInTheDocument();
    expect(screen.getByText('2000.0')).toBeInTheDocument();
  });

  it('formats dates in readable format', () => {
    render(
      <NutritionSummary 
        dailyTotals={mockDailyTotals} 
        weeklyTotal={mockWeeklyTotal}
        missingNutritionCount={0}
      />
    );

    // Check for formatted date (e.g., "Mon, Jan 15")
    expect(screen.getByText(/jan 15/i)).toBeInTheDocument();
    expect(screen.getByText(/jan 16/i)).toBeInTheDocument();
  });

  it('displays warning when recipes are missing nutrition', () => {
    render(
      <NutritionSummary 
        dailyTotals={mockDailyTotals} 
        weeklyTotal={mockWeeklyTotal}
        missingNutritionCount={3}
      />
    );

    expect(screen.getByText(/3 recipes.*missing nutrition information/i)).toBeInTheDocument();
  });

  it('uses singular form for one missing recipe', () => {
    render(
      <NutritionSummary 
        dailyTotals={mockDailyTotals} 
        weeklyTotal={mockWeeklyTotal}
        missingNutritionCount={1}
      />
    );

    expect(screen.getByText(/1 recipe.*missing nutrition information/i)).toBeInTheDocument();
  });

  it('does not display warning when no recipes are missing nutrition', () => {
    render(
      <NutritionSummary 
        dailyTotals={mockDailyTotals} 
        weeklyTotal={mockWeeklyTotal}
        missingNutritionCount={0}
      />
    );

    expect(screen.queryByText(/missing nutrition information/i)).not.toBeInTheDocument();
  });

  it('displays message when no daily data is available', () => {
    render(
      <NutritionSummary 
        dailyTotals={[]} 
        weeklyTotal={mockWeeklyTotal}
        missingNutritionCount={0}
      />
    );

    expect(screen.getByText(/no meal plan data for this period/i)).toBeInTheDocument();
  });

  it('formats decimal values to one decimal place', () => {
    const decimalWeekly = {
      calories: 12345.678,
      protein_g: 567.891,
      carbs_g: 1234.567,
      fat_g: 345.678,
      fiber_g: 123.456,
    };

    render(
      <NutritionSummary 
        dailyTotals={[]} 
        weeklyTotal={decimalWeekly}
        missingNutritionCount={0}
      />
    );

    expect(screen.getByText('12345.7')).toBeInTheDocument();
    expect(screen.getByText('567.9')).toBeInTheDocument();
    expect(screen.getByText('1234.6')).toBeInTheDocument();
    expect(screen.getByText('345.7')).toBeInTheDocument();
    expect(screen.getByText('123.5')).toBeInTheDocument();
  });

  it('handles missing values in weekly total', () => {
    const partialWeekly = {
      calories: 10000,
      protein_g: undefined,
      carbs_g: 1000,
      fat_g: undefined,
      fiber_g: 100,
    };

    render(
      <NutritionSummary 
        dailyTotals={[]} 
        weeklyTotal={partialWeekly}
        missingNutritionCount={0}
      />
    );

    expect(screen.getByText('10000.0')).toBeInTheDocument();
    expect(screen.getByText('1000.0')).toBeInTheDocument();
    expect(screen.getByText('100.0')).toBeInTheDocument();
    // Check for dashes
    const allText = screen.getByText(/weekly total/i).parentElement?.textContent || '';
    expect(allText).toContain('-');
  });
});
