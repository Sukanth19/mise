import { render, screen, fireEvent } from '@testing-library/react';
import KeyboardShortcutsHelp from './KeyboardShortcutsHelp';

describe('KeyboardShortcutsHelp', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    // Reset body overflow
    document.body.style.overflow = 'unset';
  });

  it('renders modal when isOpen is true', () => {
    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('KEYBOARD SHORTCUTS')).toBeInTheDocument();
  });

  it('does not render modal when isOpen is false', () => {
    render(<KeyboardShortcutsHelp isOpen={false} onClose={mockOnClose} />);

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('displays all keyboard shortcuts', () => {
    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Create new recipe')).toBeInTheDocument();
    expect(screen.getByText('Focus search')).toBeInTheDocument();
    expect(screen.getByText('Toggle theme')).toBeInTheDocument();
    expect(screen.getByText('Show this help')).toBeInTheDocument();
    expect(screen.getByText('Close modal')).toBeInTheDocument();
  });

  it('displays Ctrl modifier key on Windows/Linux', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'Win32',
      writable: true,
      configurable: true,
    });

    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    const ctrlKeys = screen.getAllByText('Ctrl');
    expect(ctrlKeys.length).toBeGreaterThan(0);
  });

  it('displays Cmd (⌘) modifier key on Mac', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'MacIntel',
      writable: true,
      configurable: true,
    });

    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    const cmdKeys = screen.getAllByText('⌘');
    expect(cmdKeys.length).toBeGreaterThan(0);
  });

  it('calls onClose when close button is clicked', () => {
    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button', { name: 'Close' });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when backdrop is clicked', () => {
    const { container } = render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    const backdrop = container.querySelector('.fixed.inset-0.bg-black\\/60');
    expect(backdrop).toBeInTheDocument();

    if (backdrop) {
      fireEvent.click(backdrop);
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    }
  });

  it('does not call onClose when modal content is clicked', () => {
    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    const modal = screen.getByRole('dialog');
    fireEvent.click(modal);

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('calls onClose when Escape key is pressed', () => {
    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('does not call onClose on Escape when modal is closed', () => {
    render(<KeyboardShortcutsHelp isOpen={false} onClose={mockOnClose} />);

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('prevents body scroll when modal is open', () => {
    const { rerender } = render(<KeyboardShortcutsHelp isOpen={false} onClose={mockOnClose} />);

    expect(document.body.style.overflow).toBe('unset');

    rerender(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    expect(document.body.style.overflow).toBe('hidden');
  });

  it('restores body scroll when modal is closed', () => {
    const { rerender } = render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    expect(document.body.style.overflow).toBe('hidden');

    rerender(<KeyboardShortcutsHelp isOpen={false} onClose={mockOnClose} />);

    expect(document.body.style.overflow).toBe('unset');
  });

  it('cleans up event listener on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');

    const { unmount } = render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

    removeEventListenerSpy.mockRestore();
  });

  it('has proper accessibility attributes', () => {
    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'shortcuts-title');

    const title = screen.getByText('KEYBOARD SHORTCUTS');
    expect(title).toHaveAttribute('id', 'shortcuts-title');
  });

  it('displays footer message', () => {
    render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    expect(screen.getByText('Press ? to show this help anytime')).toBeInTheDocument();
  });

  it('displays keyboard keys with proper styling', () => {
    const { container } = render(<KeyboardShortcutsHelp isOpen={true} onClose={mockOnClose} />);

    const kbdElements = container.querySelectorAll('kbd');
    expect(kbdElements.length).toBeGreaterThan(0);
  });
});
