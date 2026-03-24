import { render, screen, fireEvent } from '@testing-library/react';
import AllergenWarnings from './AllergenWarnings';

describe('AllergenWarnings', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Selector Mode', () => {
    it('renders all allergen options', () => {
      render(<AllergenWarnings selectedAllergens={[]} onChange={mockOnChange} displayMode="selector" />);

      expect(screen.getByRole('button', { name: /^🥜 nuts$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^🥛 dairy$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^🥚 eggs$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^🫘 soy$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^🌾 wheat$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^🐟 fish$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^🦐 shellfish$/i })).toBeInTheDocument();
    });

    it('displays selected allergens with active styling', () => {
      render(<AllergenWarnings selectedAllergens={['nuts', 'dairy']} onChange={mockOnChange} displayMode="selector" />);

      const nutsButton = screen.getByRole('button', { name: /nuts/i });
      const dairyButton = screen.getByRole('button', { name: /dairy/i });
      const eggsButton = screen.getByRole('button', { name: /eggs/i });

      expect(nutsButton).toHaveAttribute('aria-pressed', 'true');
      expect(dairyButton).toHaveAttribute('aria-pressed', 'true');
      expect(eggsButton).toHaveAttribute('aria-pressed', 'false');
    });

    it('calls onChange with added allergen when unselected allergen is clicked', () => {
      render(<AllergenWarnings selectedAllergens={['nuts']} onChange={mockOnChange} displayMode="selector" />);

      const dairyButton = screen.getByRole('button', { name: /dairy/i });
      fireEvent.click(dairyButton);

      expect(mockOnChange).toHaveBeenCalledWith(['nuts', 'dairy']);
    });

    it('calls onChange with removed allergen when selected allergen is clicked', () => {
      render(<AllergenWarnings selectedAllergens={['nuts', 'dairy']} onChange={mockOnChange} displayMode="selector" />);

      const nutsButton = screen.getByRole('button', { name: /nuts/i });
      fireEvent.click(nutsButton);

      expect(mockOnChange).toHaveBeenCalledWith(['dairy']);
    });

    it('displays count of selected allergens', () => {
      render(<AllergenWarnings selectedAllergens={['nuts', 'dairy', 'eggs']} onChange={mockOnChange} displayMode="selector" />);

      expect(screen.getByText(/3 allergens marked/i)).toBeInTheDocument();
    });

    it('displays singular allergen text when one allergen selected', () => {
      render(<AllergenWarnings selectedAllergens={['nuts']} onChange={mockOnChange} displayMode="selector" />);

      expect(screen.getByText(/1 allergen marked/i)).toBeInTheDocument();
    });

    it('does not display count when no allergens selected', () => {
      render(<AllergenWarnings selectedAllergens={[]} onChange={mockOnChange} displayMode="selector" />);

      expect(screen.queryByText(/marked/i)).not.toBeInTheDocument();
    });

    it('disables buttons when disabled prop is true', () => {
      render(<AllergenWarnings selectedAllergens={[]} onChange={mockOnChange} displayMode="selector" disabled={true} />);

      const nutsButton = screen.getByRole('button', { name: /nuts/i });
      expect(nutsButton).toBeDisabled();

      fireEvent.click(nutsButton);
      expect(mockOnChange).not.toHaveBeenCalled();
    });
  });

  describe('Display Mode', () => {
    it('displays prominent warning when allergens are present', () => {
      render(<AllergenWarnings selectedAllergens={['nuts', 'dairy']} displayMode="display" />);

      expect(screen.getByText(/allergen warning/i)).toBeInTheDocument();
      expect(screen.getByText(/may cause allergic reactions/i)).toBeInTheDocument();
    });

    it('displays all selected allergens in display mode', () => {
      render(<AllergenWarnings selectedAllergens={['nuts', 'dairy', 'eggs']} displayMode="display" />);

      expect(screen.getByText(/nuts/i)).toBeInTheDocument();
      expect(screen.getByText(/dairy/i)).toBeInTheDocument();
      expect(screen.getByText(/eggs/i)).toBeInTheDocument();
    });

    it('renders nothing when no allergens in display mode', () => {
      const { container } = render(<AllergenWarnings selectedAllergens={[]} displayMode="display" />);

      expect(container.firstChild).toBeNull();
    });

    it('displays warning emoji in display mode', () => {
      render(<AllergenWarnings selectedAllergens={['nuts']} displayMode="display" />);

      expect(screen.getByText('⚠️')).toBeInTheDocument();
    });
  });
});
