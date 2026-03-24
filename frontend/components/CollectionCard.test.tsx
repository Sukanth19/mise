import { render, screen, fireEvent } from '@testing-library/react';
import CollectionCard from './CollectionCard';
import { Collection } from '@/types';

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

const mockCollection: Collection = {
  id: 1,
  user_id: 1,
  name: 'Test Collection',
  description: 'Test description',
  cover_image_url: '/test-image.jpg',
  nesting_level: 0,
  recipe_count: 5,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

describe('CollectionCard', () => {
  test('renders collection name and recipe count', () => {
    render(<CollectionCard collection={mockCollection} />);
    
    expect(screen.getByText('Test Collection')).toBeInTheDocument();
    expect(screen.getByText('5 RECIPES')).toBeInTheDocument();
  });

  test('renders collection description when provided', () => {
    render(<CollectionCard collection={mockCollection} />);
    
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  test('does not render description when not provided', () => {
    const collectionWithoutDesc = { ...mockCollection, description: undefined };
    render(<CollectionCard collection={collectionWithoutDesc} />);
    
    expect(screen.queryByText('Test description')).not.toBeInTheDocument();
  });

  test('renders edit button when onEdit is provided', () => {
    const onEdit = jest.fn();
    render(<CollectionCard collection={mockCollection} onEdit={onEdit} />);
    
    const editButton = screen.getByTestId('edit-button');
    expect(editButton).toBeInTheDocument();
  });

  test('renders delete button when onDelete is provided', () => {
    const onDelete = jest.fn();
    render(<CollectionCard collection={mockCollection} onDelete={onDelete} />);
    
    const deleteButton = screen.getByTestId('delete-button');
    expect(deleteButton).toBeInTheDocument();
  });

  test('calls onEdit when edit button is clicked', () => {
    const onEdit = jest.fn();
    render(<CollectionCard collection={mockCollection} onEdit={onEdit} />);
    
    const editButton = screen.getByTestId('edit-button');
    fireEvent.click(editButton);
    
    expect(onEdit).toHaveBeenCalledWith(mockCollection);
  });

  test('calls onDelete when delete button is clicked', () => {
    const onDelete = jest.fn();
    render(<CollectionCard collection={mockCollection} onDelete={onDelete} />);
    
    const deleteButton = screen.getByTestId('delete-button');
    fireEvent.click(deleteButton);
    
    expect(onDelete).toHaveBeenCalledWith(mockCollection);
  });

  test('displays folder icon when no cover image', () => {
    const collectionWithoutImage = { ...mockCollection, cover_image_url: undefined };
    render(<CollectionCard collection={collectionWithoutImage} />);
    
    // Check for folder icon (lucide-react renders as svg)
    const folderIcon = screen.getByRole('button').querySelector('svg');
    expect(folderIcon).toBeInTheDocument();
  });

  test('displays cover image when provided', () => {
    render(<CollectionCard collection={mockCollection} />);
    
    const image = screen.getByAltText('Test Collection');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', expect.stringContaining('/test-image.jpg'));
  });

  test('handles keyboard navigation', () => {
    const { container } = render(<CollectionCard collection={mockCollection} />);
    
    const card = container.querySelector('[role="button"]');
    expect(card).toHaveAttribute('tabIndex', '0');
  });
});
