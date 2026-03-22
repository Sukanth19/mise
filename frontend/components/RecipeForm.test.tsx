import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import RecipeForm from './RecipeForm';

// Mock ImageUpload component
jest.mock('./ImageUpload', () => {
  return function MockImageUpload({ onImageUploaded, initialImageUrl }: any) {
    return (
      <div data-testid="image-upload">
        <button
          onClick={() => onImageUploaded('http://example.com/image.jpg')}
        >
          Upload Image
        </button>
        {initialImageUrl && <span>Initial: {initialImageUrl}</span>}
      </div>
    );
  };
});

describe('RecipeForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test('renders all form fields', () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByTestId('image-upload')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/ingredient 1/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/step 1/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tags/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/reference link/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save recipe/i })).toBeInTheDocument();
  });

  test('validates required title field', async () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /save recipe/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('submits form with valid data', async () => {
    mockOnSubmit.mockResolvedValue(undefined);
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Fill in title
    const titleInput = screen.getByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Recipe' } });

    // Fill in ingredient
    const ingredientInput = screen.getByPlaceholderText(/ingredient 1/i);
    fireEvent.change(ingredientInput, { target: { value: 'Flour' } });

    // Fill in step
    const stepInput = screen.getByPlaceholderText(/step 1/i);
    fireEvent.change(stepInput, { target: { value: 'Mix ingredients' } });

    // Submit form
    const submitButton = screen.getByRole('button', { name: /save recipe/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Recipe',
        ingredients: ['Flour'],
        steps: ['Mix ingredients'],
        image_url: undefined,
        tags: undefined,
        reference_link: undefined,
      });
    });
  });

  test('adds and removes ingredients', () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Initially one ingredient field
    expect(screen.getByPlaceholderText(/ingredient 1/i)).toBeInTheDocument();

    // Add ingredient
    const addButton = screen.getByRole('button', { name: /add ingredient/i });
    fireEvent.click(addButton);

    expect(screen.getByPlaceholderText(/ingredient 2/i)).toBeInTheDocument();

    // Remove ingredient
    const removeButtons = screen.getAllByRole('button', { name: /remove ingredient/i });
    fireEvent.click(removeButtons[1]);

    expect(screen.queryByPlaceholderText(/ingredient 2/i)).not.toBeInTheDocument();
  });

  test('adds and removes steps', () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Initially one step field
    expect(screen.getByPlaceholderText(/step 1/i)).toBeInTheDocument();

    // Add step
    const addButton = screen.getByRole('button', { name: /add step/i });
    fireEvent.click(addButton);

    expect(screen.getByPlaceholderText(/step 2/i)).toBeInTheDocument();

    // Remove step
    const removeButtons = screen.getAllByRole('button', { name: /remove step/i });
    fireEvent.click(removeButtons[1]);

    expect(screen.queryByPlaceholderText(/step 2/i)).not.toBeInTheDocument();
  });

  test('prevents removing last ingredient', () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    const removeButton = screen.getByRole('button', { name: /remove ingredient 1/i });
    expect(removeButton).toBeDisabled();
  });

  test('prevents removing last step', () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    const removeButton = screen.getByRole('button', { name: /remove step 1/i });
    expect(removeButton).toBeDisabled();
  });

  test('handles image upload', async () => {
    mockOnSubmit.mockResolvedValue(undefined);
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Upload image
    const uploadButton = screen.getByRole('button', { name: /upload image/i });
    fireEvent.click(uploadButton);

    // Fill in required fields
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByPlaceholderText(/ingredient 1/i), { target: { value: 'Flour' } });
    fireEvent.change(screen.getByPlaceholderText(/step 1/i), { target: { value: 'Mix' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /save recipe/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          image_url: 'http://example.com/image.jpg',
        })
      );
    });
  });

  test('parses tags correctly', async () => {
    mockOnSubmit.mockResolvedValue(undefined);
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Fill in required fields
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByPlaceholderText(/ingredient 1/i), { target: { value: 'Flour' } });
    fireEvent.change(screen.getByPlaceholderText(/step 1/i), { target: { value: 'Mix' } });
    fireEvent.change(screen.getByLabelText(/tags/i), { 
      target: { value: 'dinner, vegetarian, quick' } 
    });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /save recipe/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          tags: ['dinner', 'vegetarian', 'quick'],
        })
      );
    });
  });

  test('filters out empty ingredients and steps', async () => {
    mockOnSubmit.mockResolvedValue(undefined);
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Fill in title
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test' } });

    // Add multiple ingredients, some empty
    fireEvent.click(screen.getByRole('button', { name: /add ingredient/i }));
    fireEvent.click(screen.getByRole('button', { name: /add ingredient/i }));
    fireEvent.change(screen.getByPlaceholderText(/ingredient 1/i), { target: { value: 'Flour' } });
    fireEvent.change(screen.getByPlaceholderText(/ingredient 2/i), { target: { value: '' } });
    fireEvent.change(screen.getByPlaceholderText(/ingredient 3/i), { target: { value: 'Sugar' } });

    // Add multiple steps, some empty
    fireEvent.click(screen.getByRole('button', { name: /add step/i }));
    fireEvent.change(screen.getByPlaceholderText(/step 1/i), { target: { value: 'Mix' } });
    fireEvent.change(screen.getByPlaceholderText(/step 2/i), { target: { value: '' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /save recipe/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          ingredients: ['Flour', 'Sugar'],
          steps: ['Mix'],
        })
      );
    });
  });

  test('pre-populates form with initial data', () => {
    const initialData = {
      title: 'Existing Recipe',
      image_url: 'http://example.com/existing.jpg',
      ingredients: ['Flour', 'Sugar'],
      steps: ['Mix', 'Bake'],
      tags: ['dessert', 'easy'],
      reference_link: 'http://example.com/recipe',
    };

    render(<RecipeForm onSubmit={mockOnSubmit} initialData={initialData} />);

    expect(screen.getByLabelText(/title/i)).toHaveValue('Existing Recipe');
    expect(screen.getByText(/initial: http:\/\/example\.com\/existing\.jpg/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('Flour')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Sugar')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Mix')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Bake')).toBeInTheDocument();
    expect(screen.getByLabelText(/tags/i)).toHaveValue('dessert, easy');
    expect(screen.getByLabelText(/reference link/i)).toHaveValue('http://example.com/recipe');
  });

  test('displays error message on submission failure', async () => {
    mockOnSubmit.mockRejectedValue(new Error('Network error'));
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Fill in required fields
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByPlaceholderText(/ingredient 1/i), { target: { value: 'Flour' } });
    fireEvent.change(screen.getByPlaceholderText(/step 1/i), { target: { value: 'Mix' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /save recipe/i }));

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });

  test('disables submit button while submitting', async () => {
    mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Fill in required fields
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByPlaceholderText(/ingredient 1/i), { target: { value: 'Flour' } });
    fireEvent.change(screen.getByPlaceholderText(/step 1/i), { target: { value: 'Mix' } });

    // Submit
    const submitButton = screen.getByRole('button', { name: /save recipe/i });
    fireEvent.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/saving\.\.\./i)).toBeInTheDocument();

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  test('uses custom submit label', () => {
    render(<RecipeForm onSubmit={mockOnSubmit} submitLabel="Update Recipe" />);

    expect(screen.getByRole('button', { name: /update recipe/i })).toBeInTheDocument();
  });

  test('validates at least one ingredient is required', async () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Fill in title and step but leave ingredient empty
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByPlaceholderText(/step 1/i), { target: { value: 'Mix' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /save recipe/i }));

    await waitFor(() => {
      expect(screen.getByText(/at least one ingredient is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('validates at least one step is required', async () => {
    render(<RecipeForm onSubmit={mockOnSubmit} />);

    // Fill in title and ingredient but leave step empty
    fireEvent.change(screen.getByLabelText(/title/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByPlaceholderText(/ingredient 1/i), { target: { value: 'Flour' } });

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /save recipe/i }));

    await waitFor(() => {
      expect(screen.getByText(/at least one step is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });
});
