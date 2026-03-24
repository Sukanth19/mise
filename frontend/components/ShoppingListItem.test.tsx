import { render, screen, fireEvent } from '@testing-library/react';
import ShoppingListItem from './ShoppingListItem';
import { ShoppingListItem as ShoppingListItemType } from '@/types';

describe('ShoppingListItem', () => {
  const mockItem: ShoppingListItemType = {
    id: 1,
    shopping_list_id: 1,
    ingredient_name: 'Tomatoes',
    quantity: '2 lbs',
    category: 'produce',
    is_checked: false,
    is_custom: false,
    created_at: '2024-01-01T00:00:00Z',
  };

  it('renders item with name and quantity', () => {
    render(<ShoppingListItem item={mockItem} />);
    
    expect(screen.getByText('Tomatoes')).toBeInTheDocument();
    expect(screen.getByText('2 lbs')).toBeInTheDocument();
  });

  it('renders checkbox in unchecked state', () => {
    render(<ShoppingListItem item={mockItem} />);
    
    const checkbox = screen.getByTestId('item-checkbox') as HTMLInputElement;
    expect(checkbox).toBeInTheDocument();
    expect(checkbox.checked).toBe(false);
  });

  it('renders checkbox in checked state', () => {
    const checkedItem = { ...mockItem, is_checked: true };
    render(<ShoppingListItem item={checkedItem} />);
    
    const checkbox = screen.getByTestId('item-checkbox') as HTMLInputElement;
    expect(checkbox.checked).toBe(true);
  });

  it('calls onCheck when checkbox is clicked', () => {
    const onCheck = jest.fn();
    render(<ShoppingListItem item={mockItem} onCheck={onCheck} />);
    
    const checkbox = screen.getByTestId('item-checkbox');
    fireEvent.click(checkbox);
    
    expect(onCheck).toHaveBeenCalledWith(1, true);
  });

  it('calls onCheck with false when unchecking', () => {
    const onCheck = jest.fn();
    const checkedItem = { ...mockItem, is_checked: true };
    render(<ShoppingListItem item={checkedItem} onCheck={onCheck} />);
    
    const checkbox = screen.getByTestId('item-checkbox');
    fireEvent.click(checkbox);
    
    expect(onCheck).toHaveBeenCalledWith(1, false);
  });

  it('applies strikethrough style when checked', () => {
    const checkedItem = { ...mockItem, is_checked: true };
    render(<ShoppingListItem item={checkedItem} />);
    
    const itemName = screen.getByText('Tomatoes');
    expect(itemName).toHaveClass('line-through');
  });

  it('applies opacity when checked', () => {
    const checkedItem = { ...mockItem, is_checked: true };
    render(<ShoppingListItem item={checkedItem} />);
    
    const container = screen.getByTestId('shopping-list-item');
    expect(container).toHaveClass('opacity-60');
  });

  it('shows delete button for custom items', () => {
    const customItem = { ...mockItem, is_custom: true };
    const onDelete = jest.fn();
    render(<ShoppingListItem item={customItem} onDelete={onDelete} />);
    
    expect(screen.getByTestId('delete-button')).toBeInTheDocument();
  });

  it('does not show delete button for non-custom items', () => {
    render(<ShoppingListItem item={mockItem} />);
    
    expect(screen.queryByTestId('delete-button')).not.toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', () => {
    const customItem = { ...mockItem, is_custom: true };
    const onDelete = jest.fn();
    render(<ShoppingListItem item={customItem} onDelete={onDelete} />);
    
    const deleteButton = screen.getByTestId('delete-button');
    fireEvent.click(deleteButton);
    
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it('renders without quantity if not provided', () => {
    const itemWithoutQuantity = { ...mockItem, quantity: undefined };
    render(<ShoppingListItem item={itemWithoutQuantity} />);
    
    expect(screen.getByText('Tomatoes')).toBeInTheDocument();
    expect(screen.queryByText('2 lbs')).not.toBeInTheDocument();
  });

  it('has accessible checkbox label', () => {
    render(<ShoppingListItem item={mockItem} />);
    
    const checkbox = screen.getByLabelText('Check Tomatoes');
    expect(checkbox).toBeInTheDocument();
  });

  it('has accessible delete button label for custom items', () => {
    const customItem = { ...mockItem, is_custom: true };
    const onDelete = jest.fn();
    render(<ShoppingListItem item={customItem} onDelete={onDelete} />);
    
    const deleteButton = screen.getByLabelText('Delete Tomatoes');
    expect(deleteButton).toBeInTheDocument();
  });
});
