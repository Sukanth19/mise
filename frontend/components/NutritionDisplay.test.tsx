import { render, screen } from '@testing-library/react';
import NutritionDisplay from './NutritionDisplay';

describe('NutritionDisplay', () => {
  const mockNutritionFacts = {
    calories: 500,
    protein_g: 25,
    carbs_g: 60,
    fat_g: 15,
    fiber_g: 8,
  };

  const mockPerServing = {
    calories: 125,
    protein_g: 6.25,
    carbs_g: 15,
    fat_g: 3.75,
    fiber_g: 2,
  };

  it('displays nutrition facts when provided', () => {
    render(<NutritionDisplay nutritionFacts={mockNutritionFacts} />);

    expect(screen.getByText(/nutrition facts/i)).toBeInTheDocument();
    expect(screen.getByText('500.0')).toBeInTheDocument();
    expect(screen.getByText('25.0')).toBeInTheDocument();
    expect(screen.getByText('60.0')).toBeInTheDocument();
    expect(screen.getByText('15.0')).toBeInTheDocument();
    expect(screen.getByText('8.0')).toBeInTheDocument();
  });

  it('displays per-serving nutrition when provided', () => {
    render(
      <NutritionDisplay 
        nutritionFacts={mockNutritionFacts} 
        perServing={mockPerServing}
        servings={4}
      />
    );

    expect(screen.getByText(/per serving/i)).toBeInTheDocument();
    expect(screen.getByText('125.0')).toBeInTheDocument();
    expect(screen.getByText('6.3')).toBeInTheDocument(); // 6.25 rounds to 6.3
  });

  it('displays servings count in total section', () => {
    render(
      <NutritionDisplay 
        nutritionFacts={mockNutritionFacts} 
        servings={4}
      />
    );

    expect(screen.getByText(/4 servings/i)).toBeInTheDocument();
  });

  it('hides per-serving section when showPerServing is false', () => {
    render(
      <NutritionDisplay 
        nutritionFacts={mockNutritionFacts} 
        perServing={mockPerServing}
        showPerServing={false}
      />
    );

    expect(screen.queryByText(/per serving/i)).not.toBeInTheDocument();
  });

  it('displays message when no nutrition facts provided', () => {
    render(<NutritionDisplay nutritionFacts={null} />);

    expect(screen.getByText(/no nutrition information available/i)).toBeInTheDocument();
  });

  it('displays message when nutrition facts are empty', () => {
    render(<NutritionDisplay nutritionFacts={{}} />);

    expect(screen.getByText(/no nutrition information available/i)).toBeInTheDocument();
  });

  it('displays dash for missing values', () => {
    const partialNutrition = {
      calories: 300,
      protein_g: undefined,
      carbs_g: 40,
      fat_g: undefined,
      fiber_g: 5,
    };

    render(<NutritionDisplay nutritionFacts={partialNutrition} />);

    expect(screen.getByText('300.0')).toBeInTheDocument();
    expect(screen.getByText('40.0')).toBeInTheDocument();
    expect(screen.getByText('5.0')).toBeInTheDocument();
    // Check for dashes (there should be multiple)
    const allText = screen.getByText(/nutrition facts/i).parentElement?.textContent || '';
    expect(allText).toContain('-');
  });

  it('formats decimal values to one decimal place', () => {
    const decimalNutrition = {
      calories: 123.456,
      protein_g: 12.789,
      carbs_g: 45.123,
      fat_g: 8.999,
      fiber_g: 3.111,
    };

    render(<NutritionDisplay nutritionFacts={decimalNutrition} />);

    expect(screen.getByText('123.5')).toBeInTheDocument();
    expect(screen.getByText('12.8')).toBeInTheDocument();
    expect(screen.getByText('45.1')).toBeInTheDocument();
    expect(screen.getByText('9.0')).toBeInTheDocument();
    expect(screen.getByText('3.1')).toBeInTheDocument();
  });
});
