import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FilterPanel, { FilterOptions } from './FilterPanel';

describe('FilterPanel', () => {
  const mockOnFilterChange = jest.fn();
  const mockAvailableTags = ['breakfast', 'lunch', 'dinner', 'dessert'];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Filter Selection', () => {
    it('should toggle favorites filter', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      const favoritesCheckbox = screen.getByRole('checkbox', { name: /favorites only/i });
      
      // Initially unchecked
      expect(favoritesCheckbox).not.toBeChecked();

      // Click to enable favorites filter
      fireEvent.click(favoritesCheckbox);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            favorites: true,
          })
        );
      });

      // Click again to disable favorites filter
      fireEvent.click(favoritesCheckbox);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            favorites: undefined,
          })
        );
      });
    });

    it('should update minimum rating filter', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Expand the filter panel to access rating slider
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      const ratingSlider = screen.getByRole('slider');
      
      // Change rating to 4
      fireEvent.change(ratingSlider, { target: { value: '4' } });
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            minRating: 4,
          })
        );
      });
    });

    it('should select and deselect tags', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Expand the filter panel
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      // Select a tag
      const breakfastTag = screen.getByRole('button', { name: /breakfast/i });
      fireEvent.click(breakfastTag);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            tags: ['breakfast'],
          })
        );
      });

      // Select another tag
      const lunchTag = screen.getByRole('button', { name: /lunch/i });
      fireEvent.click(lunchTag);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            tags: expect.arrayContaining(['breakfast', 'lunch']),
          })
        );
      });

      // Deselect first tag
      fireEvent.click(breakfastTag);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            tags: ['lunch'],
          })
        );
      });
    });

    it('should select dietary labels', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Expand the filter panel
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      // Select vegan label
      const veganLabel = screen.getByRole('button', { name: /^vegan$/i });
      fireEvent.click(veganLabel);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            dietaryLabels: ['vegan'],
          })
        );
      });
    });

    it('should select allergens to exclude', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Expand the filter panel
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      // Select nuts allergen
      const nutsAllergen = screen.getByRole('button', { name: /^nuts$/i });
      fireEvent.click(nutsAllergen);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            excludeAllergens: ['nuts'],
          })
        );
      });
    });
  });

  describe('Filter Combination', () => {
    it('should combine multiple filters', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Enable favorites
      const favoritesCheckbox = screen.getByRole('checkbox', { name: /favorites only/i });
      fireEvent.click(favoritesCheckbox);

      // Expand panel
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      // Set minimum rating
      const ratingSlider = screen.getByRole('slider');
      fireEvent.change(ratingSlider, { target: { value: '3' } });

      // Select a tag
      const breakfastTag = screen.getByRole('button', { name: /breakfast/i });
      fireEvent.click(breakfastTag);

      // Select dietary label
      const veganLabel = screen.getByRole('button', { name: /^vegan$/i });
      fireEvent.click(veganLabel);

      // Select allergen to exclude
      const nutsAllergen = screen.getByRole('button', { name: /^nuts$/i });
      fireEvent.click(nutsAllergen);

      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            favorites: true,
            minRating: 3,
            tags: ['breakfast'],
            dietaryLabels: ['vegan'],
            excludeAllergens: ['nuts'],
          })
        );
      });
    });

    it('should clear all filters', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Enable favorites
      const favoritesCheckbox = screen.getByRole('checkbox', { name: /favorites only/i });
      fireEvent.click(favoritesCheckbox);

      // Expand panel
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      // Set minimum rating
      const ratingSlider = screen.getByRole('slider');
      fireEvent.change(ratingSlider, { target: { value: '4' } });

      // Wait for filters to be applied
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalled();
      });

      // Clear all filters
      const clearButton = screen.getByRole('button', { name: /clear all/i });
      fireEvent.click(clearButton);

      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            favorites: undefined,
            minRating: undefined,
            tags: undefined,
            dietaryLabels: undefined,
            excludeAllergens: undefined,
            sortBy: 'date',
            sortOrder: 'desc',
          })
        );
      });
    });
  });

  describe('Sort Selection', () => {
    it('should change sort field', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      const sortSelect = screen.getByRole('combobox');
      
      // Change to rating sort
      fireEvent.change(sortSelect, { target: { value: 'rating' } });
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            sortBy: 'rating',
          })
        );
      });

      // Change to title sort
      fireEvent.change(sortSelect, { target: { value: 'title' } });
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            sortBy: 'title',
          })
        );
      });
    });

    it('should toggle sort order', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Find the sort order toggle button by its text content
      const sortOrderButton = screen.getByText('↓');
      
      // Initially descending
      expect(sortOrderButton).toHaveTextContent('↓');

      // Toggle to ascending
      fireEvent.click(sortOrderButton);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            sortOrder: 'asc',
          })
        );
      });

      // Toggle back to descending
      fireEvent.click(sortOrderButton);
      
      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            sortOrder: 'desc',
          })
        );
      });
    });

    it('should combine sort with filters', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Enable favorites
      const favoritesCheckbox = screen.getByRole('checkbox', { name: /favorites only/i });
      fireEvent.click(favoritesCheckbox);

      // Change sort to rating
      const sortSelect = screen.getByRole('combobox');
      fireEvent.change(sortSelect, { target: { value: 'rating' } });

      // Toggle sort order to ascending
      const sortOrderButton = screen.getByText('↓');
      fireEvent.click(sortOrderButton);

      await waitFor(() => {
        expect(mockOnFilterChange).toHaveBeenCalledWith(
          expect.objectContaining({
            favorites: true,
            sortBy: 'rating',
            sortOrder: 'asc',
          })
        );
      });
    });
  });

  describe('UI Behavior', () => {
    it('should expand and collapse filter panel', () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Initially collapsed - rating slider should not be visible
      expect(screen.queryByRole('slider')).not.toBeInTheDocument();

      // Expand
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      // Now rating slider should be visible
      expect(screen.getByRole('slider')).toBeInTheDocument();

      // Collapse
      const collapseButton = screen.getByRole('button', { name: /collapse/i });
      fireEvent.click(collapseButton);

      // Rating slider should be hidden again
      expect(screen.queryByRole('slider')).not.toBeInTheDocument();
    });

    it('should show clear all button only when filters are active', async () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={mockAvailableTags} />);

      // Initially no clear button (no active filters)
      expect(screen.queryByRole('button', { name: /clear all/i })).not.toBeInTheDocument();

      // Enable favorites
      const favoritesCheckbox = screen.getByRole('checkbox', { name: /favorites only/i });
      fireEvent.click(favoritesCheckbox);

      // Now clear button should appear
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /clear all/i })).toBeInTheDocument();
      });
    });

    it('should not show tags section when no tags available', () => {
      render(<FilterPanel onFilterChange={mockOnFilterChange} availableTags={[]} />);

      // Expand panel
      const expandButton = screen.getByRole('button', { name: /expand/i });
      fireEvent.click(expandButton);

      // Tags section should not be present
      expect(screen.queryByText(/^tags$/i)).not.toBeInTheDocument();
    });
  });
});
