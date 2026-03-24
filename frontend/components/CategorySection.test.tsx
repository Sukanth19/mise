import { render, screen, fireEvent } from '@testing-library/react';
import CategorySection from './CategorySection';
import { ShoppingListItem } from '@/types';

describe('CategorySection', () => {
  const mockItems: ShoppingListItem[] = [
    {
      id: 1,
      shopping_list_id: 1,
      ingredient_name: 'Tomatoes',
      quantity: '2 lbs',
      category: 'produce',
      is_checked: false,
      is_custom: false,
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      shopping_list_id: 1,
      ingredient_name: 'Lettuce',
      quantity: '1 head',
      category: 'produce',
      is_checked: true,
      is_custom: false,
      created_at: '2024-01-01T00:00:00Z',
    },
  ];

  it('renders category label correctly', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    expect(screen.getByText('Produce')).toBeInTheDocument();
  });

  it('displays item count', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    expect(screen.getByText('(2)')).toBeInTheDocument();
  });

  it('renders all items in the category', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    expect(screen.getByText('Tomatoes')).toBeInTheDocument();
    expect(screen.getByText('Lettuce')).toBeInTheDocument();
  });

  it('starts in expanded state', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    const itemsContainer = screen.getByTestId('category-items');
    expect(itemsContainer).toBeInTheDocument();
  });

  it('collapses when header is clicked', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    const header = screen.getByTestId('category-header');
    fireEvent.click(header);
    
    expect(screen.queryByTestId('category-items')).not.toBeInTheDocument();
  });

  it('expands when header is clicked again', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    const header = screen.getByTestId('category-header');
    
    // Collapse
    fireEvent.click(header);
    expect(screen.queryByTestId('category-items')).not.toBeInTheDocument();
    
    // Expand
    fireEvent.click(header);
    expect(screen.getByTestId('category-items')).toBeInTheDocument();
  });

  it('passes onItemCheck to child items', () => {
    const onItemCheck = jest.fn();
    render(
      <CategorySection 
        category="produce" 
        items={mockItems} 
        onItemCheck={onItemCheck}
      />
    );
    
    const checkboxes = screen.getAllByTestId('item-checkbox');
    fireEvent.click(checkboxes[0]);
    
    expect(onItemCheck).toHaveBeenCalledWith(1, true);
  });

  it('passes onItemDelete to child items', () => {
    const customItem: ShoppingListItem = {
      ...mockItems[0],
      is_custom: true,
    };
    const onItemDelete = jest.fn();
    
    render(
      <CategorySection 
        category="produce" 
        items={[customItem]} 
        onItemDelete={onItemDelete}
      />
    );
    
    const deleteButton = screen.getByTestId('delete-button');
    fireEvent.click(deleteButton);
    
    expect(onItemDelete).toHaveBeenCalledWith(1);
  });

  it('renders correct label for dairy category', () => {
    render(<CategorySection category="dairy" items={mockItems} />);
    
    expect(screen.getByText('Dairy')).toBeInTheDocument();
  });

  it('renders correct label for meat category', () => {
    render(<CategorySection category="meat" items={mockItems} />);
    
    expect(screen.getByText('Meat & Seafood')).toBeInTheDocument();
  });

  it('renders correct label for pantry category', () => {
    render(<CategorySection category="pantry" items={mockItems} />);
    
    expect(screen.getByText('Pantry')).toBeInTheDocument();
  });

  it('renders correct label for other category', () => {
    render(<CategorySection category="other" items={mockItems} />);
    
    expect(screen.getByText('Other')).toBeInTheDocument();
  });

  it('renders empty category with zero items', () => {
    render(<CategorySection category="produce" items={[]} />);
    
    expect(screen.getByText('(0)')).toBeInTheDocument();
  });

  it('has accessible aria-expanded attribute', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    const header = screen.getByTestId('category-header');
    expect(header).toHaveAttribute('aria-expanded', 'true');
    
    fireEvent.click(header);
    expect(header).toHaveAttribute('aria-expanded', 'false');
  });

  it('has accessible aria-controls attribute', () => {
    render(<CategorySection category="produce" items={mockItems} />);
    
    const header = screen.getByTestId('category-header');
    expect(header).toHaveAttribute('aria-controls', 'category-produce-items');
  });
});
