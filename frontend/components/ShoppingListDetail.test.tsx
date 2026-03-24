import { render, screen, fireEvent } from '@testing-library/react';
import ShoppingListDetail from './ShoppingListDetail';
import { ShoppingList } from '@/types';

jest.mock('./CategorySection', () => {
  return function MockCategorySection({ category, items }: any) {
    return (
      <div data-testid={`category-${category}`}>
        {items.map((item: any) => (
          <div key={item.id}>{item.ingredient_name}</div>
        ))}
      </div>
    );
  };
});

describe('ShoppingListDetail', () => {
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
        is_checked: true,
        is_custom: false,
        created_at: '2024-01-15T10:00:00Z',
      },
      {
        id: 2,
        shopping_list_id: 1,
        ingredient_name: 'Apples',
        quantity: '6',
        category: 'produce',
        is_checked: false,
        is_custom: false,
        created_at: '2024-01-15T10:00:00Z',
      },
      {
        id: 3,
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
    render(<ShoppingListDetail shoppingList={mockShoppingList} />);
    expect(screen.getByText('Weekly Groceries')).toBeInTheDocument();
  });

  it('displays progress correctly', () => {
    render(<ShoppingListDetail shoppingList={mockShoppingList} />);
    expect(screen.getByText('1 / 3 ITEMS')).toBeInTheDocument();
  });

  it('calculates progress percentage correctly', () => {
    render(<ShoppingListDetail shoppingList={mockShoppingList} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '33.33333333333333');
  });

  it('renders share button when onShare is provided', () => {
    const onShare = jest.fn();
    render(<ShoppingListDetail shoppingList={mockShoppingList} onShare={onShare} />);
    expect(screen.getByTestId('share-button')).toBeInTheDocument();
  });

  it('calls onShare when share button is clicked', () => {
    const onShare = jest.fn();
    render(<ShoppingListDetail shoppingList={mockShoppingList} onShare={onShare} />);
    
    const shareButton = screen.getByTestId('share-button');
    fireEvent.click(shareButton);
    
    expect(onShare).toHaveBeenCalled();
  });

  it('does not render share button when onShare is not provided', () => {
    render(<ShoppingListDetail shoppingList={mockShoppingList} />);
    expect(screen.queryByTestId('share-button')).not.toBeInTheDocument();
  });

  it('renders category sections for items', () => {
    render(<ShoppingListDetail shoppingList={mockShoppingList} />);
    expect(screen.getByTestId('category-dairy')).toBeInTheDocument();
    expect(screen.getByTestId('category-produce')).toBeInTheDocument();
    expect(screen.getByTestId('category-pantry')).toBeInTheDocument();
  });

  it('displays empty state when no items', () => {
    const emptyList: ShoppingList = {
      ...mockShoppingList,
      items: [],
    };
    render(<ShoppingListDetail shoppingList={emptyList} />);
    expect(screen.getByText('No items in this shopping list yet.')).toBeInTheDocument();
  });

  it('handles 100% progress', () => {
    const allCheckedList: ShoppingList = {
      ...mockShoppingList,
      items: mockShoppingList.items?.map(item => ({ ...item, is_checked: true })),
    };
    render(<ShoppingListDetail shoppingList={allCheckedList} />);
    expect(screen.getByText('3 / 3 ITEMS')).toBeInTheDocument();
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '100');
  });

  it('handles 0% progress', () => {
    const noneCheckedList: ShoppingList = {
      ...mockShoppingList,
      items: mockShoppingList.items?.map(item => ({ ...item, is_checked: false })),
    };
    render(<ShoppingListDetail shoppingList={noneCheckedList} />);
    expect(screen.getByText('0 / 3 ITEMS')).toBeInTheDocument();
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '0');
  });
});
