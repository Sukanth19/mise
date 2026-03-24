import { render, screen, fireEvent } from '@testing-library/react';
import DietaryLabelsSelector from './DietaryLabelsSelector';

describe('DietaryLabelsSelector', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all dietary label options', () => {
    render(<DietaryLabelsSelector selectedLabels={[]} onChange={mockOnChange} />);

    expect(screen.getByRole('button', { name: /vegan/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /vegetarian/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /gluten-free/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /dairy-free/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /keto/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /paleo/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /low-carb/i })).toBeInTheDocument();
  });

  it('displays selected labels with active styling', () => {
    render(<DietaryLabelsSelector selectedLabels={['vegan', 'gluten-free']} onChange={mockOnChange} />);

    const veganButton = screen.getByRole('button', { name: /vegan/i });
    const glutenFreeButton = screen.getByRole('button', { name: /gluten-free/i });
    const vegetarianButton = screen.getByRole('button', { name: /vegetarian/i });

    expect(veganButton).toHaveAttribute('aria-pressed', 'true');
    expect(glutenFreeButton).toHaveAttribute('aria-pressed', 'true');
    expect(vegetarianButton).toHaveAttribute('aria-pressed', 'false');
  });

  it('calls onChange with added label when unselected label is clicked', () => {
    render(<DietaryLabelsSelector selectedLabels={['vegan']} onChange={mockOnChange} />);

    const vegetarianButton = screen.getByRole('button', { name: /vegetarian/i });
    fireEvent.click(vegetarianButton);

    expect(mockOnChange).toHaveBeenCalledWith(['vegan', 'vegetarian']);
  });

  it('calls onChange with removed label when selected label is clicked', () => {
    render(<DietaryLabelsSelector selectedLabels={['vegan', 'vegetarian']} onChange={mockOnChange} />);

    const veganButton = screen.getByRole('button', { name: /vegan/i });
    fireEvent.click(veganButton);

    expect(mockOnChange).toHaveBeenCalledWith(['vegetarian']);
  });

  it('displays count of selected labels', () => {
    render(<DietaryLabelsSelector selectedLabels={['vegan', 'keto', 'paleo']} onChange={mockOnChange} />);

    expect(screen.getByText(/3 labels selected/i)).toBeInTheDocument();
  });

  it('displays singular label text when one label selected', () => {
    render(<DietaryLabelsSelector selectedLabels={['vegan']} onChange={mockOnChange} />);

    expect(screen.getByText(/1 label selected/i)).toBeInTheDocument();
  });

  it('does not display count when no labels selected', () => {
    render(<DietaryLabelsSelector selectedLabels={[]} onChange={mockOnChange} />);

    expect(screen.queryByText(/selected/i)).not.toBeInTheDocument();
  });

  it('disables buttons when disabled prop is true', () => {
    render(<DietaryLabelsSelector selectedLabels={[]} onChange={mockOnChange} disabled={true} />);

    const veganButton = screen.getByRole('button', { name: /vegan/i });
    expect(veganButton).toBeDisabled();

    fireEvent.click(veganButton);
    expect(mockOnChange).not.toHaveBeenCalled();
  });

  it('allows multiple labels to be selected', () => {
    const { rerender } = render(<DietaryLabelsSelector selectedLabels={[]} onChange={mockOnChange} />);

    fireEvent.click(screen.getByRole('button', { name: /vegan/i }));
    expect(mockOnChange).toHaveBeenCalledWith(['vegan']);

    rerender(<DietaryLabelsSelector selectedLabels={['vegan']} onChange={mockOnChange} />);

    fireEvent.click(screen.getByRole('button', { name: /gluten-free/i }));
    expect(mockOnChange).toHaveBeenCalledWith(['vegan', 'gluten-free']);
  });
});
