import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NutritionForm, { NutritionData } from './NutritionForm';
import NutritionDisplay from './NutritionDisplay';
import DietaryLabelsSelector from './DietaryLabelsSelector';
import AllergenWarnings from './AllergenWarnings';

/**
 * Unit tests for nutrition components integration
 * Tests cover:
 * - NutritionForm validation
 * - Per-serving calculation display
 * - Dietary labels selection
 * - Allergen warnings display
 */

describe('NutritionForm', () => {
  it('validates non-negative nutrition values', async () => {
    const mockSubmit = jest.fn();
    render(<NutritionForm onSubmit={mockSubmit} />);

    // Try to submit negative calories
    const caloriesInput = screen.getByLabelText(/calories/i);
    fireEvent.change(caloriesInput, { target: { value: '-100' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/cannot be negative/i)).toBeInTheDocument();
    });

    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it('validates serving size is positive', async () => {
    const mockSubmit = jest.fn();
    render(<NutritionForm onSubmit={mockSubmit} />);

    const servingsInput = screen.getByLabelText(/serving size/i);
    fireEvent.change(servingsInput, { target: { value: '0' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/serving size must be a positive number/i)).toBeInTheDocument();
    });

    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it('submits valid nutrition data', async () => {
    const mockSubmit = jest.fn().mockResolvedValue(undefined);
    render(<NutritionForm onSubmit={mockSubmit} />);

    // Fill in valid data
    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '4' } });
    fireEvent.change(screen.getByLabelText(/calories/i), { target: { value: '500' } });
    fireEvent.change(screen.getByLabelText(/protein/i), { target: { value: '25' } });
    fireEvent.change(screen.getByLabelText(/carbs/i), { target: { value: '60' } });
    fireEvent.change(screen.getByLabelText(/fat/i), { target: { value: '15' } });
    fireEvent.change(screen.getByLabelText(/fiber/i), { target: { value: '8' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        calories: 500,
        protein_g: 25,
        carbs_g: 60,
        fat_g: 15,
        fiber_g: 8,
        servings: 4,
      });
    });
  });

  it('allows optional nutrition fields to be empty', async () => {
    const mockSubmit = jest.fn().mockResolvedValue(undefined);
    render(<NutritionForm onSubmit={mockSubmit} />);

    // Only fill servings (required)
    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '2' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        servings: 2,
        calories: undefined,
        protein_g: undefined,
        carbs_g: undefined,
        fat_g: undefined,
        fiber_g: undefined,
      });
    });
  });

  it('displays error message on submission failure', async () => {
    const mockSubmit = jest.fn().mockRejectedValue(new Error('Network error'));
    render(<NutritionForm onSubmit={mockSubmit} />);

    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '1' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });

  it('calls onCancel when cancel button is clicked', () => {
    const mockCancel = jest.fn();
    render(<NutritionForm onSubmit={jest.fn()} onCancel={mockCancel} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockCancel).toHaveBeenCalled();
  });
});

describe('NutritionDisplay', () => {
  it('displays per-serving calculation correctly', () => {
    const nutritionFacts = {
      id: 1,
      recipe_id: 1,
      calories: 800,
      protein_g: 40,
      carbs_g: 100,
      fat_g: 20,
      fiber_g: 16,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    const perServing = {
      id: 1,
      recipe_id: 1,
      calories: 200,
      protein_g: 10,
      carbs_g: 25,
      fat_g: 5,
      fiber_g: 4,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    render(
      <NutritionDisplay
        nutritionFacts={nutritionFacts}
        perServing={perServing}
        servings={4}
        showPerServing={true}
      />
    );

    // Check total values
    expect(screen.getByText(/total recipe/i)).toBeInTheDocument();
    expect(screen.getByText('800.0')).toBeInTheDocument(); // Total calories

    // Check per-serving values
    expect(screen.getByText(/per serving/i)).toBeInTheDocument();
    expect(screen.getByText('200.0')).toBeInTheDocument(); // Per-serving calories
  });

  it('shows message when no nutrition data available', () => {
    render(<NutritionDisplay nutritionFacts={null} />);

    expect(screen.getByText(/no nutrition information available/i)).toBeInTheDocument();
  });

  it('hides per-serving section when showPerServing is false', () => {
    const nutritionFacts = {
      id: 1,
      recipe_id: 1,
      calories: 800,
      protein_g: 40,
      carbs_g: 100,
      fat_g: 20,
      fiber_g: 16,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    render(
      <NutritionDisplay
        nutritionFacts={nutritionFacts}
        showPerServing={false}
      />
    );

    expect(screen.queryByText(/per serving/i)).not.toBeInTheDocument();
  });

  it('displays servings count in total section', () => {
    const nutritionFacts = {
      id: 1,
      recipe_id: 1,
      calories: 800,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    render(
      <NutritionDisplay
        nutritionFacts={nutritionFacts}
        servings={6}
      />
    );

    expect(screen.getByText(/6 servings/i)).toBeInTheDocument();
  });
});

describe('DietaryLabelsSelector', () => {
  it('renders all dietary label options', () => {
    render(<DietaryLabelsSelector selectedLabels={[]} onChange={jest.fn()} />);

    expect(screen.getByText(/vegan/i)).toBeInTheDocument();
    expect(screen.getByText(/vegetarian/i)).toBeInTheDocument();
    expect(screen.getByText(/gluten-free/i)).toBeInTheDocument();
    expect(screen.getByText(/dairy-free/i)).toBeInTheDocument();
    expect(screen.getByText(/keto/i)).toBeInTheDocument();
    expect(screen.getByText(/paleo/i)).toBeInTheDocument();
    expect(screen.getByText(/low-carb/i)).toBeInTheDocument();
  });

  it('toggles label selection on click', () => {
    const mockOnChange = jest.fn();
    render(<DietaryLabelsSelector selectedLabels={[]} onChange={mockOnChange} />);

    const veganButton = screen.getByRole('button', { name: /vegan/i });
    fireEvent.click(veganButton);

    expect(mockOnChange).toHaveBeenCalledWith(['vegan']);
  });

  it('removes label when clicked again', () => {
    const mockOnChange = jest.fn();
    render(<DietaryLabelsSelector selectedLabels={['vegan']} onChange={mockOnChange} />);

    const veganButton = screen.getByRole('button', { name: /vegan/i });
    fireEvent.click(veganButton);

    expect(mockOnChange).toHaveBeenCalledWith([]);
  });

  it('allows multiple label selection', () => {
    const mockOnChange = jest.fn();
    const { rerender } = render(
      <DietaryLabelsSelector selectedLabels={[]} onChange={mockOnChange} />
    );

    // Select vegan
    fireEvent.click(screen.getByRole('button', { name: /vegan/i }));
    expect(mockOnChange).toHaveBeenCalledWith(['vegan']);

    // Rerender with vegan selected
    rerender(<DietaryLabelsSelector selectedLabels={['vegan']} onChange={mockOnChange} />);

    // Select gluten-free
    fireEvent.click(screen.getByRole('button', { name: /gluten-free/i }));
    expect(mockOnChange).toHaveBeenCalledWith(['vegan', 'gluten-free']);
  });

  it('displays count of selected labels', () => {
    render(<DietaryLabelsSelector selectedLabels={['vegan', 'keto']} onChange={jest.fn()} />);

    expect(screen.getByText(/2 labels selected/i)).toBeInTheDocument();
  });

  it('disables buttons when disabled prop is true', () => {
    render(<DietaryLabelsSelector selectedLabels={[]} onChange={jest.fn()} disabled={true} />);

    const veganButton = screen.getByRole('button', { name: /vegan/i });
    expect(veganButton).toBeDisabled();
  });
});

describe('AllergenWarnings', () => {
  describe('Selector mode', () => {
    it('renders all allergen options', () => {
      render(
        <AllergenWarnings
          selectedAllergens={[]}
          onChange={jest.fn()}
          displayMode="selector"
        />
      );

      expect(screen.getByText('Nuts')).toBeInTheDocument();
      expect(screen.getByText('Dairy')).toBeInTheDocument();
      expect(screen.getByText('Eggs')).toBeInTheDocument();
      expect(screen.getByText('Soy')).toBeInTheDocument();
      expect(screen.getByText('Wheat')).toBeInTheDocument();
      expect(screen.getByText('Fish')).toBeInTheDocument();
      expect(screen.getByText('Shellfish')).toBeInTheDocument();
    });

    it('toggles allergen selection on click', () => {
      const mockOnChange = jest.fn();
      render(
        <AllergenWarnings
          selectedAllergens={[]}
          onChange={mockOnChange}
          displayMode="selector"
        />
      );

      const nutsButton = screen.getByRole('button', { name: /nuts/i });
      fireEvent.click(nutsButton);

      expect(mockOnChange).toHaveBeenCalledWith(['nuts']);
    });

    it('displays warning count when allergens selected', () => {
      render(
        <AllergenWarnings
          selectedAllergens={['nuts', 'dairy']}
          onChange={jest.fn()}
          displayMode="selector"
        />
      );

      expect(screen.getByText(/2 allergens marked/i)).toBeInTheDocument();
    });
  });

  describe('Display mode', () => {
    it('displays prominent allergen warning', () => {
      render(
        <AllergenWarnings
          selectedAllergens={['nuts', 'dairy']}
          displayMode="display"
        />
      );

      expect(screen.getByText(/allergen warning/i)).toBeInTheDocument();
      expect(screen.getByText(/may cause allergic reactions/i)).toBeInTheDocument();
      expect(screen.getByText(/nuts/i)).toBeInTheDocument();
      expect(screen.getByText(/dairy/i)).toBeInTheDocument();
    });

    it('renders nothing when no allergens in display mode', () => {
      const { container } = render(
        <AllergenWarnings
          selectedAllergens={[]}
          displayMode="display"
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('displays warning emoji', () => {
      render(
        <AllergenWarnings
          selectedAllergens={['nuts']}
          displayMode="display"
        />
      );

      expect(screen.getByText('⚠️')).toBeInTheDocument();
    });
  });
});

describe('Nutrition Integration', () => {
  it('NutritionForm and NutritionDisplay work together', async () => {
    const mockSubmit = jest.fn().mockResolvedValue(undefined);
    const { rerender } = render(<NutritionForm onSubmit={mockSubmit} />);

    // Submit nutrition data
    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '4' } });
    fireEvent.change(screen.getByLabelText(/calories/i), { target: { value: '800' } });
    fireEvent.change(screen.getByLabelText(/protein/i), { target: { value: '40' } });

    fireEvent.click(screen.getByRole('button', { name: /save nutrition facts/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalled();
    });

    const submittedData = mockSubmit.mock.calls[0][0];

    // Now display the data
    const nutritionFacts = {
      id: 1,
      recipe_id: 1,
      calories: submittedData.calories,
      protein_g: submittedData.protein_g,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    const perServing = {
      id: 1,
      recipe_id: 1,
      calories: submittedData.calories! / submittedData.servings!,
      protein_g: submittedData.protein_g! / submittedData.servings!,
      created_at: '2024-01-01',
      updated_at: '2024-01-01',
    };

    rerender(
      <NutritionDisplay
        nutritionFacts={nutritionFacts}
        perServing={perServing}
        servings={submittedData.servings}
      />
    );

    // Verify display shows correct values
    expect(screen.getByText('800.0')).toBeInTheDocument(); // Total calories
    expect(screen.getByText('200.0')).toBeInTheDocument(); // Per-serving calories (800/4)
  });

  it('Dietary labels and allergen warnings can be used together', () => {
    const mockDietaryChange = jest.fn();
    const mockAllergenChange = jest.fn();

    const { container } = render(
      <div>
        <DietaryLabelsSelector
          selectedLabels={['vegan']}
          onChange={mockDietaryChange}
        />
        <AllergenWarnings
          selectedAllergens={['nuts']}
          onChange={mockAllergenChange}
          displayMode="selector"
        />
      </div>
    );

    // Both components should be present
    expect(screen.getByText(/dietary labels/i)).toBeInTheDocument();
    expect(screen.getByText(/allergen warnings/i)).toBeInTheDocument();

    // Verify selections are shown
    expect(screen.getByText(/1 label selected/i)).toBeInTheDocument();
    expect(screen.getByText(/1 allergen marked/i)).toBeInTheDocument();
  });
});
