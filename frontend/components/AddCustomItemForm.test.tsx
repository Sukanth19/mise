import { render, screen, fireEvent } from '@testing-library/react';
import AddCustomItemForm from './AddCustomItemForm';

describe('AddCustomItemForm', () => {
  it('renders form with all fields', () => {
    render(<AddCustomItemForm onAdd={jest.fn()} />);
    
    expect(screen.getByLabelText(/ITEM NAME/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/QUANTITY/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/CATEGORY/i)).toBeInTheDocument();
    expect(screen.getByTestId('add-button')).toBeInTheDocument();
  });

  it('has required attribute on ingredient name field', () => {
    render(<AddCustomItemForm onAdd={jest.fn()} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    expect(ingredientInput).toHaveAttribute('required');
  });

  it('does not have required attribute on quantity field', () => {
    render(<AddCustomItemForm onAdd={jest.fn()} />);
    
    const quantityInput = screen.getByTestId('quantity-input');
    expect(quantityInput).not.toHaveAttribute('required');
  });

  it('calls onAdd with correct data when form is submitted', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    const quantityInput = screen.getByTestId('quantity-input');
    const categorySelect = screen.getByTestId('category-select');
    const addButton = screen.getByTestId('add-button');
    
    fireEvent.change(ingredientInput, { target: { value: 'Paper towels' } });
    fireEvent.change(quantityInput, { target: { value: '2 rolls' } });
    fireEvent.change(categorySelect, { target: { value: 'pantry' } });
    fireEvent.click(addButton);
    
    expect(onAdd).toHaveBeenCalledWith({
      ingredient_name: 'Paper towels',
      quantity: '2 rolls',
      category: 'pantry',
    });
  });

  it('calls onAdd without quantity when quantity is empty', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    const addButton = screen.getByTestId('add-button');
    
    fireEvent.change(ingredientInput, { target: { value: 'Milk' } });
    fireEvent.click(addButton);
    
    expect(onAdd).toHaveBeenCalledWith({
      ingredient_name: 'Milk',
      quantity: undefined,
      category: 'other',
    });
  });

  it('trims whitespace from ingredient name', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    const addButton = screen.getByTestId('add-button');
    
    fireEvent.change(ingredientInput, { target: { value: '  Bread  ' } });
    fireEvent.click(addButton);
    
    expect(onAdd).toHaveBeenCalledWith({
      ingredient_name: 'Bread',
      quantity: undefined,
      category: 'other',
    });
  });

  it('trims whitespace from quantity', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    const quantityInput = screen.getByTestId('quantity-input');
    const addButton = screen.getByTestId('add-button');
    
    fireEvent.change(ingredientInput, { target: { value: 'Eggs' } });
    fireEvent.change(quantityInput, { target: { value: '  1 dozen  ' } });
    fireEvent.click(addButton);
    
    expect(onAdd).toHaveBeenCalledWith({
      ingredient_name: 'Eggs',
      quantity: '1 dozen',
      category: 'other',
    });
  });

  it('does not call onAdd when ingredient name is empty', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const addButton = screen.getByTestId('add-button');
    fireEvent.click(addButton);
    
    expect(onAdd).not.toHaveBeenCalled();
  });

  it('does not call onAdd when ingredient name is only whitespace', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    const addButton = screen.getByTestId('add-button');
    
    fireEvent.change(ingredientInput, { target: { value: '   ' } });
    fireEvent.click(addButton);
    
    expect(onAdd).not.toHaveBeenCalled();
  });

  it('resets form after successful submission', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input') as HTMLInputElement;
    const quantityInput = screen.getByTestId('quantity-input') as HTMLInputElement;
    const categorySelect = screen.getByTestId('category-select') as HTMLSelectElement;
    const addButton = screen.getByTestId('add-button');
    
    fireEvent.change(ingredientInput, { target: { value: 'Butter' } });
    fireEvent.change(quantityInput, { target: { value: '1 stick' } });
    fireEvent.change(categorySelect, { target: { value: 'dairy' } });
    fireEvent.click(addButton);
    
    expect(ingredientInput.value).toBe('');
    expect(quantityInput.value).toBe('');
    expect(categorySelect.value).toBe('other');
  });

  it('has all category options', () => {
    render(<AddCustomItemForm onAdd={jest.fn()} />);
    
    const categorySelect = screen.getByTestId('category-select');
    const options = Array.from(categorySelect.querySelectorAll('option'));
    const optionValues = options.map(opt => opt.value);
    
    expect(optionValues).toEqual(['produce', 'dairy', 'meat', 'pantry', 'other']);
  });

  it('defaults to "other" category', () => {
    render(<AddCustomItemForm onAdd={jest.fn()} />);
    
    const categorySelect = screen.getByTestId('category-select') as HTMLSelectElement;
    expect(categorySelect.value).toBe('other');
  });

  it('has correct placeholder for ingredient name', () => {
    render(<AddCustomItemForm onAdd={jest.fn()} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    expect(ingredientInput).toHaveAttribute('placeholder', 'e.g., Paper towels');
  });

  it('has correct placeholder for quantity', () => {
    render(<AddCustomItemForm onAdd={jest.fn()} />);
    
    const quantityInput = screen.getByTestId('quantity-input');
    expect(quantityInput).toHaveAttribute('placeholder', 'e.g., 2 rolls');
  });

  it('submits form on Enter key in ingredient field', () => {
    const onAdd = jest.fn();
    render(<AddCustomItemForm onAdd={onAdd} />);
    
    const ingredientInput = screen.getByTestId('ingredient-name-input');
    
    fireEvent.change(ingredientInput, { target: { value: 'Cheese' } });
    fireEvent.submit(ingredientInput.closest('form')!);
    
    expect(onAdd).toHaveBeenCalledWith({
      ingredient_name: 'Cheese',
      quantity: undefined,
      category: 'other',
    });
  });
});
