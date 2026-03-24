import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CollectionForm from './CollectionForm';
import { Collection } from '@/types';

// Mock ImageUpload component
jest.mock('./ImageUpload', () => {
  return function MockImageUpload({ onImageUploaded }: any) {
    return (
      <button
        type="button"
        onClick={() => onImageUploaded('/mock-image.jpg')}
      >
        Mock Upload
      </button>
    );
  };
});

const mockCollections: Collection[] = [
  {
    id: 1,
    user_id: 1,
    name: 'Parent Collection',
    nesting_level: 0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    user_id: 1,
    name: 'Level 1 Collection',
    nesting_level: 1,
    parent_collection_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 3,
    user_id: 1,
    name: 'Level 2 Collection',
    nesting_level: 2,
    parent_collection_id: 2,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

describe('CollectionForm', () => {
  test('renders form fields', () => {
    const onSubmit = jest.fn();
    render(<CollectionForm onSubmit={onSubmit} />);
    
    expect(screen.getByLabelText(/collection name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByText(/cover image/i)).toBeInTheDocument();
  });

  test('shows validation error when name is empty', async () => {
    const onSubmit = jest.fn();
    render(<CollectionForm onSubmit={onSubmit} />);
    
    const submitButton = screen.getByRole('button', { name: /save collection/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/collection name is required/i)).toBeInTheDocument();
    });
    
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('submits form with valid data', async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<CollectionForm onSubmit={onSubmit} />);
    
    const nameInput = screen.getByLabelText(/collection name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    
    fireEvent.change(nameInput, { target: { value: 'New Collection' } });
    fireEvent.change(descriptionInput, { target: { value: 'Test description' } });
    
    const submitButton = screen.getByRole('button', { name: /save collection/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'New Collection',
        description: 'Test description',
        cover_image_url: undefined,
        parent_collection_id: undefined,
      });
    });
  });

  test('populates form with initial data', () => {
    const onSubmit = jest.fn();
    const initialData = {
      name: 'Existing Collection',
      description: 'Existing description',
      cover_image_url: '/existing-image.jpg',
    };
    
    render(<CollectionForm onSubmit={onSubmit} initialData={initialData} />);
    
    expect(screen.getByDisplayValue('Existing Collection')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Existing description')).toBeInTheDocument();
  });

  test('shows parent collection selector when collections available', () => {
    const onSubmit = jest.fn();
    render(
      <CollectionForm 
        onSubmit={onSubmit} 
        availableCollections={mockCollections}
      />
    );
    
    expect(screen.getByLabelText(/parent collection/i)).toBeInTheDocument();
  });

  test('validates nesting level (max 3)', async () => {
    const onSubmit = jest.fn();
    render(
      <CollectionForm 
        onSubmit={onSubmit} 
        availableCollections={mockCollections}
      />
    );
    
    const nameInput = screen.getByLabelText(/collection name/i);
    fireEvent.change(nameInput, { target: { value: 'New Collection' } });
    
    // Try to select a level 2 collection as parent (would create level 3, which is max but allowed)
    // We need to test with a collection that's already at level 2 to trigger the error
    const parentSelect = screen.getByLabelText(/parent collection/i);
    
    // Level 2 collection should not be in the selector (filtered out)
    const options = Array.from(parentSelect.querySelectorAll('option'));
    const level2Option = options.find(opt => opt.textContent?.includes('Level 2 Collection'));
    
    // Level 2 collections should be filtered out from parent selector
    expect(level2Option).toBeUndefined();
  });

  test('filters out collections at max nesting level from parent selector', () => {
    const onSubmit = jest.fn();
    render(
      <CollectionForm 
        onSubmit={onSubmit} 
        availableCollections={mockCollections}
      />
    );
    
    const parentSelect = screen.getByLabelText(/parent collection/i);
    const options = Array.from(parentSelect.querySelectorAll('option'));
    
    // Should not include Level 2 Collection (nesting_level = 2)
    expect(options.find(opt => opt.textContent?.includes('Level 2 Collection'))).toBeUndefined();
    
    // Should include Parent Collection and Level 1 Collection
    expect(options.find(opt => opt.textContent?.includes('Parent Collection'))).toBeDefined();
    expect(options.find(opt => opt.textContent?.includes('Level 1 Collection'))).toBeDefined();
  });

  test('excludes current collection from parent selector', () => {
    const onSubmit = jest.fn();
    render(
      <CollectionForm 
        onSubmit={onSubmit} 
        availableCollections={mockCollections}
        currentCollectionId={1}
      />
    );
    
    const parentSelect = screen.getByLabelText(/parent collection/i);
    const options = Array.from(parentSelect.querySelectorAll('option'));
    
    // Should not include the current collection (id: 1)
    expect(options.find(opt => opt.value === '1')).toBeUndefined();
  });

  test('handles image upload', async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<CollectionForm onSubmit={onSubmit} />);
    
    const nameInput = screen.getByLabelText(/collection name/i);
    fireEvent.change(nameInput, { target: { value: 'New Collection' } });
    
    // Trigger mock image upload
    const uploadButton = screen.getByText('Mock Upload');
    fireEvent.click(uploadButton);
    
    const submitButton = screen.getByRole('button', { name: /save collection/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: 'New Collection',
        description: undefined,
        cover_image_url: '/mock-image.jpg',
        parent_collection_id: undefined,
      });
    });
  });

  test('displays custom submit label', () => {
    const onSubmit = jest.fn();
    render(<CollectionForm onSubmit={onSubmit} submitLabel="Create New Collection" />);
    
    expect(screen.getByRole('button', { name: /create new collection/i })).toBeInTheDocument();
  });

  test('disables submit button while submitting', async () => {
    const onSubmit = jest.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    render(<CollectionForm onSubmit={onSubmit} />);
    
    const nameInput = screen.getByLabelText(/collection name/i);
    fireEvent.change(nameInput, { target: { value: 'New Collection' } });
    
    const submitButton = screen.getByRole('button', { name: /save collection/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/saving/i)).toBeInTheDocument();
    });
  });
});
