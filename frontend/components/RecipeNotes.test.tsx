import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RecipeNotes from './RecipeNotes';
import { apiClient } from '@/lib/api';
import { Note } from '@/types';

// Mock the API client
jest.mock('@/lib/api', () => ({
  apiClient: jest.fn(),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Trash2: () => <span>Trash Icon</span>,
  Plus: () => <span>Plus Icon</span>,
}));

describe('RecipeNotes', () => {
  const mockRecipeId = 1;
  const mockNotes: Note[] = [
    {
      id: 1,
      recipe_id: mockRecipeId,
      user_id: 1,
      note_text: 'This is a great recipe!',
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 2,
      recipe_id: mockRecipeId,
      user_id: 1,
      note_text: 'Added extra garlic and it was delicious.',
      created_at: '2024-01-16T14:20:00Z',
      updated_at: '2024-01-16T14:20:00Z',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock window.confirm
    global.confirm = jest.fn(() => true);
  });

  describe('Note Display', () => {
    it('should display all notes in chronological order', () => {
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      expect(screen.getByText('This is a great recipe!')).toBeInTheDocument();
      expect(screen.getByText('Added extra garlic and it was delicious.')).toBeInTheDocument();
    });

    it('should display empty state when no notes exist', () => {
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      expect(screen.getByText(/No notes yet/i)).toBeInTheDocument();
    });

    it('should format note dates correctly', () => {
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      // Check that dates are displayed (format may vary by locale)
      const dateElements = screen.getAllByText(/Jan|2024/);
      expect(dateElements.length).toBeGreaterThan(0);
    });

    it('should display delete button for each note', () => {
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      const deleteButtons = screen.getAllByLabelText('Delete note');
      expect(deleteButtons).toHaveLength(2);
    });
  });

  describe('Note Creation', () => {
    it('should render note input form', () => {
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      expect(screen.getByPlaceholderText(/Add a personal note/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /ADD NOTE/i })).toBeInTheDocument();
    });

    it('should add a new note when form is submitted', async () => {
      const newNote: Note = {
        id: 3,
        recipe_id: mockRecipeId,
        user_id: 1,
        note_text: 'New test note',
        created_at: '2024-01-17T12:00:00Z',
        updated_at: '2024-01-17T12:00:00Z',
      };

      (apiClient as jest.Mock).mockResolvedValueOnce(newNote);

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      const textarea = screen.getByPlaceholderText(/Add a personal note/i);
      const submitButton = screen.getByRole('button', { name: /ADD NOTE/i });

      fireEvent.change(textarea, { target: { value: 'New test note' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(apiClient).toHaveBeenCalledWith(`/api/recipes/${mockRecipeId}/notes`, {
          method: 'POST',
          body: JSON.stringify({ note_text: 'New test note' }),
        });
      });

      await waitFor(() => {
        expect(screen.getByText('New test note')).toBeInTheDocument();
      });
    });

    it('should clear input after successful note creation', async () => {
      const newNote: Note = {
        id: 3,
        recipe_id: mockRecipeId,
        user_id: 1,
        note_text: 'New test note',
        created_at: '2024-01-17T12:00:00Z',
        updated_at: '2024-01-17T12:00:00Z',
      };

      (apiClient as jest.Mock).mockResolvedValueOnce(newNote);

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      const textarea = screen.getByPlaceholderText(/Add a personal note/i) as HTMLTextAreaElement;
      const submitButton = screen.getByRole('button', { name: /ADD NOTE/i });

      fireEvent.change(textarea, { target: { value: 'New test note' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(textarea.value).toBe('');
      });
    });

    it('should show error when trying to add empty note', async () => {
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      const textarea = screen.getByPlaceholderText(/Add a personal note/i);
      const submitButton = screen.getByRole('button', { name: /ADD NOTE/i });
      
      // Initially button should be disabled with empty text
      expect(submitButton).toBeDisabled();
      
      // Add some text then remove it
      fireEvent.change(textarea, { target: { value: 'test' } });
      expect(submitButton).not.toBeDisabled();
      
      fireEvent.change(textarea, { target: { value: '' } });
      expect(submitButton).toBeDisabled();
    });

    it('should trim whitespace from note text', async () => {
      const newNote: Note = {
        id: 3,
        recipe_id: mockRecipeId,
        user_id: 1,
        note_text: 'Trimmed note',
        created_at: '2024-01-17T12:00:00Z',
        updated_at: '2024-01-17T12:00:00Z',
      };

      (apiClient as jest.Mock).mockResolvedValueOnce(newNote);

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      const textarea = screen.getByPlaceholderText(/Add a personal note/i);
      const submitButton = screen.getByRole('button', { name: /ADD NOTE/i });

      fireEvent.change(textarea, { target: { value: '  Trimmed note  ' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(apiClient).toHaveBeenCalledWith(`/api/recipes/${mockRecipeId}/notes`, {
          method: 'POST',
          body: JSON.stringify({ note_text: 'Trimmed note' }),
        });
      });
    });

    it('should disable submit button while submitting', async () => {
      const newNote: Note = {
        id: 3,
        recipe_id: mockRecipeId,
        user_id: 1,
        note_text: 'New test note',
        created_at: '2024-01-17T12:00:00Z',
        updated_at: '2024-01-17T12:00:00Z',
      };

      let resolvePromise: (value: Note) => void;
      const promise = new Promise<Note>((resolve) => {
        resolvePromise = resolve;
      });
      (apiClient as jest.Mock).mockReturnValueOnce(promise);

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      const textarea = screen.getByPlaceholderText(/Add a personal note/i);
      const submitButton = screen.getByRole('button', { name: /ADD NOTE/i });

      fireEvent.change(textarea, { target: { value: 'New test note' } });
      fireEvent.click(submitButton);

      // Should be disabled while submitting
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/ADDING.../i)).toBeInTheDocument();

      // Resolve the promise
      resolvePromise!(newNote);

      await waitFor(() => {
        expect(screen.getByText(/ADD NOTE/i)).toBeInTheDocument();
      });
    });

    it('should handle API errors when creating note', async () => {
      (apiClient as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      const textarea = screen.getByPlaceholderText(/Add a personal note/i);
      const submitButton = screen.getByRole('button', { name: /ADD NOTE/i });

      fireEvent.change(textarea, { target: { value: 'New test note' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/Network error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Note Deletion', () => {
    it('should delete a note when delete button is clicked', async () => {
      (apiClient as jest.Mock).mockResolvedValueOnce({ message: 'Note deleted successfully' });

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      const deleteButtons = screen.getAllByLabelText('Delete note');
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(apiClient).toHaveBeenCalledWith(`/api/recipes/${mockRecipeId}/notes/1`, {
          method: 'DELETE',
        });
      });

      await waitFor(() => {
        expect(screen.queryByText('This is a great recipe!')).not.toBeInTheDocument();
      });
    });

    it('should show confirmation dialog before deleting', async () => {
      const confirmSpy = jest.spyOn(window, 'confirm');
      
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      const deleteButtons = screen.getAllByLabelText('Delete note');
      fireEvent.click(deleteButtons[0]);

      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this note?');
    });

    it('should not delete note if confirmation is cancelled', async () => {
      global.confirm = jest.fn(() => false);

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      const deleteButtons = screen.getAllByLabelText('Delete note');
      fireEvent.click(deleteButtons[0]);

      expect(apiClient).not.toHaveBeenCalled();
      expect(screen.getByText('This is a great recipe!')).toBeInTheDocument();
    });

    it('should handle API errors when deleting note', async () => {
      (apiClient as jest.Mock).mockRejectedValueOnce(new Error('Delete failed'));
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      const deleteButtons = screen.getAllByLabelText('Delete note');
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Delete failed');
      });

      // Note should still be visible
      expect(screen.getByText('This is a great recipe!')).toBeInTheDocument();

      alertSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={mockNotes} />);

      const deleteButtons = screen.getAllByLabelText('Delete note');
      expect(deleteButtons).toHaveLength(2);
    });

    it('should disable form elements when submitting', async () => {
      const newNote: Note = {
        id: 3,
        recipe_id: mockRecipeId,
        user_id: 1,
        note_text: 'New test note',
        created_at: '2024-01-17T12:00:00Z',
        updated_at: '2024-01-17T12:00:00Z',
      };

      let resolvePromise: (value: Note) => void;
      const promise = new Promise<Note>((resolve) => {
        resolvePromise = resolve;
      });
      (apiClient as jest.Mock).mockReturnValueOnce(promise);

      render(<RecipeNotes recipeId={mockRecipeId} initialNotes={[]} />);

      const textarea = screen.getByPlaceholderText(/Add a personal note/i);
      const submitButton = screen.getByRole('button', { name: /ADD NOTE/i });

      fireEvent.change(textarea, { target: { value: 'New test note' } });
      fireEvent.click(submitButton);

      // Should be disabled while submitting
      expect(textarea).toBeDisabled();
      expect(submitButton).toBeDisabled();

      // Resolve the promise
      resolvePromise!(newNote);

      await waitFor(() => {
        expect(textarea).not.toBeDisabled();
      });
    });
  });
});
