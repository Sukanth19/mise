import { render, screen, fireEvent } from '@testing-library/react';
import ShoppingListCard from './ShoppingListCard';
import { ShoppingList } from '@/types';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

describe('ShoppingListCard', () => {
  const mockShoppingList: ShoppingList = {
    id: 1,
    user_id: 1,
    name: 'Weekly Groceries',
    created_at: '2024-01-15T10:00:00Z',
    items: [
      {
        id: 1,
        shopping_list_id: 1,
        ingredient_name: 'Milk',
        quantity: '1 gallon',
        category: 'dairy',
        is_checked: false,
        is_custom: false,
        created_at: '2024-01-15T10:00:00Z',
      },
      {
        id: 2,
        shopping_list_id: 1,
        ingredient_name: 'Bread',
        quantity: '1 loaf',
        category: 'pantry',
        is_checked: false,
        is_custom: false,
        created_at: '2024-01-15T10:00:00Z',
      },
    ],
  };

  it('renders shopping list name', () => {
    render(<ShoppingListCard shoppingList={mockShoppingList} />);
    expect(screen.getByText('Weekly Groceries')).toBeInTheDocument();
  });

  it('displays item count', () => {
    render(<ShoppingListCard shoppingList={mockShoppingList} />);
    expect(screen.getByText('2 ITEMS')).toBeInTheDocument();
  });

  it('displays creation date', () => {
    render(<ShoppingListCard shoppingList={mockShoppingList} />);
    const dateElement = screen.getByText(/1\/15\/2024/);
    expect(dateElement).toBeInTheDocument();
  });

  it('displays view button', () => {
    render(<ShoppingListCard shoppingList={mockShoppingList} />);
    expect(screen.getByTestId('view-button')).toBeInTheDocument();
  });

  it('calls onShare when share button is clicked', () => {
    const onShare = jest.fn();
    render(<ShoppingListCard shoppingList={mockShoppingList} onShare={onShare} />);
    
    const shareButton = screen.getByTestId('share-button');
    fireEvent.click(shareButton);
    
    expect(onShare).toHaveBeenCalledWith(mockShoppingList);
  });

  it('calls onDelete when delete button is clicked', () => {
    const onDelete = jest.fn();
    render(<ShoppingListCard shoppingList={mockShoppingList} onDelete={onDelete} />);
    
    const deleteButton = screen.getByTestId('delete-button');
    fireEvent.click(deleteButton);
    
    expect(onDelete).toHaveBeenCalledWith(mockShoppingList);
  });

  it('does not render share button when onShare is not provided', () => {
    render(<ShoppingListCard shoppingList={mockShoppingList} />);
    expect(screen.queryByTestId('share-button')).not.toBeInTheDocument();
  });

  it('does not render delete button when onDelete is not provided', () => {
    render(<ShoppingListCard shoppingList={mockShoppingList} />);
    expect(screen.queryByTestId('delete-button')).not.toBeInTheDocument();
  });

  it('handles shopping list with no items', () => {
    const emptyList: ShoppingList = {
      ...mockShoppingList,
      items: [],
    };
    render(<ShoppingListCard shoppingList={emptyList} />);
    expect(screen.getByText('0 ITEMS')).toBeInTheDocument();
  });

  it('handles shopping list with undefined items', () => {
    const listWithoutItems: ShoppingList = {
      ...mockShoppingList,
      items: undefined,
    };
    render(<ShoppingListCard shoppingList={listWithoutItems} />);
    expect(screen.getByText('0 ITEMS')).toBeInTheDocument();
  });
});
