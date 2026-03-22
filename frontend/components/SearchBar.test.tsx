import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchBar from './SearchBar';

describe('SearchBar', () => {
  jest.useFakeTimers();

  it('renders search input with placeholder', () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText('Search recipes...');
    expect(input).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} placeholder="Find a recipe..." />);

    const input = screen.getByPlaceholderText('Find a recipe...');
    expect(input).toBeInTheDocument();
  });

  it('updates input value on change', () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText('Search recipes...') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'pasta' } });

    expect(input.value).toBe('pasta');
  });

  it('debounces search callback by 300ms', async () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText('Search recipes...');
    
    // Type multiple characters quickly
    fireEvent.change(input, { target: { value: 'p' } });
    fireEvent.change(input, { target: { value: 'pa' } });
    fireEvent.change(input, { target: { value: 'pas' } });
    fireEvent.change(input, { target: { value: 'past' } });
    fireEvent.change(input, { target: { value: 'pasta' } });

    // Should not call immediately
    expect(mockOnSearch).not.toHaveBeenCalled();

    // Fast-forward time by 300ms
    jest.advanceTimersByTime(300);

    // Should call once with final value
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledTimes(1);
      expect(mockOnSearch).toHaveBeenCalledWith('pasta');
    });
  });

  it('calls onSearch with empty string when input is cleared', async () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText('Search recipes...');
    
    fireEvent.change(input, { target: { value: 'pasta' } });
    jest.advanceTimersByTime(300);

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith('pasta');
    });

    mockOnSearch.mockClear();

    fireEvent.change(input, { target: { value: '' } });
    jest.advanceTimersByTime(300);

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith('');
    });
  });

  afterEach(() => {
    jest.clearAllTimers();
  });
});
