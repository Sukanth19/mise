import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import NutritionForm from './NutritionForm';

describe('NutritionForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form with all nutrition fields', () => {
    render(<NutritionForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/serving size/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/calories/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/protein/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/carbs/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/fat/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/fiber/i)).toBeInTheDocument();
  });

  it('displays initial data when provided', () => {
    const initialData = {
      calories: 500,
      protein_g: 25,
      carbs_g: 60,
      fat_g: 15,
      fiber_g: 8,
      servings: 4,
    };

    render(<NutritionForm initialData={initialData} onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/serving size/i)).toHaveValue(4);
    expect(screen.getByLabelText(/calories/i)).toHaveValue(500);
    expect(screen.getByLabelText(/protein/i)).toHaveValue(25);
    expect(screen.getByLabelText(/carbs/i)).toHaveValue(60);
    expect(screen.getByLabelText(/fat/i)).toHaveValue(15);
    expect(screen.getByLabelText(/fiber/i)).toHaveValue(8);
  });

  it('validates non-negative values for nutrition fields', async () => {
    render(<NutritionForm onSubmit={mockOnSubmit} />);

    const caloriesInput = screen.getByLabelText(/calories/i);
    fireEvent.change(caloriesInput, { target: { value: '-100' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/cannot be negative/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates serving size is positive', async () => {
    render(<NutritionForm onSubmit={mockOnSubmit} />);

    const servingsInput = screen.getByLabelText(/serving size/i);
    fireEvent.change(servingsInput, { target: { value: '0' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/serving size must be a positive number/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits form with valid data', async () => {
    mockOnSubmit.mockResolvedValue(undefined);

    render(<NutritionForm onSubmit={mockOnSubmit} />);

    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '2' } });
    fireEvent.change(screen.getByLabelText(/calories/i), { target: { value: '400' } });
    fireEvent.change(screen.getByLabelText(/protein/i), { target: { value: '20' } });
    fireEvent.change(screen.getByLabelText(/carbs/i), { target: { value: '50' } });
    fireEvent.change(screen.getByLabelText(/fat/i), { target: { value: '10' } });
    fireEvent.change(screen.getByLabelText(/fiber/i), { target: { value: '5' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        calories: 400,
        protein_g: 20,
        carbs_g: 50,
        fat_g: 10,
        fiber_g: 5,
        servings: 2,
      });
    });
  });

  it('allows empty optional fields', async () => {
    mockOnSubmit.mockResolvedValue(undefined);

    render(<NutritionForm onSubmit={mockOnSubmit} />);

    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '1' } });
    fireEvent.change(screen.getByLabelText(/calories/i), { target: { value: '300' } });
    // Leave other fields empty

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        calories: 300,
        protein_g: undefined,
        carbs_g: undefined,
        fat_g: undefined,
        fiber_g: undefined,
        servings: 1,
      });
    });
  });

  it('displays error message on submit failure', async () => {
    mockOnSubmit.mockRejectedValue(new Error('Network error'));

    render(<NutritionForm onSubmit={mockOnSubmit} />);

    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '1' } });
    fireEvent.change(screen.getByLabelText(/calories/i), { target: { value: '300' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(<NutritionForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('disables buttons while submitting', async () => {
    mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<NutritionForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    fireEvent.change(screen.getByLabelText(/serving size/i), { target: { value: '1' } });

    const submitButton = screen.getByRole('button', { name: /save nutrition facts/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeDisabled();
    });
  });
});
