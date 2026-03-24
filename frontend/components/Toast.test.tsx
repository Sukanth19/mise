import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Toast, { useToast } from './Toast';
import { renderHook, act } from '@testing-library/react';

describe('Toast', () => {
  it('renders success variant with green styling', () => {
    const onClose = jest.fn();
    const { container } = render(
      <Toast
        message="Success message"
        type="success"
        isVisible={true}
        onClose={onClose}
      />
    );

    expect(screen.getByText('Success message')).toBeInTheDocument();
    expect(screen.getByText('✓')).toBeInTheDocument();
    expect(container.querySelector('.bg-success')).toBeInTheDocument();
  });

  it('renders error variant with red styling', () => {
    const onClose = jest.fn();
    const { container } = render(
      <Toast
        message="Error message"
        type="error"
        isVisible={true}
        onClose={onClose}
      />
    );

    expect(screen.getByText('Error message')).toBeInTheDocument();
    expect(screen.getByText('✗')).toBeInTheDocument();
    expect(container.querySelector('.bg-destructive')).toBeInTheDocument();
  });

  it('auto-dismisses after 3 seconds by default', async () => {
    jest.useFakeTimers();
    const onClose = jest.fn();
    
    render(
      <Toast
        message="Auto dismiss"
        isVisible={true}
        onClose={onClose}
      />
    );

    expect(onClose).not.toHaveBeenCalled();
    
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    expect(onClose).toHaveBeenCalledTimes(1);
    
    jest.useRealTimers();
  });

  it('allows manual dismiss via close button', () => {
    const onClose = jest.fn();
    
    render(
      <Toast
        message="Manual dismiss"
        isVisible={true}
        onClose={onClose}
      />
    );

    const closeButton = screen.getByRole('button', { name: 'Close notification' });
    fireEvent.click(closeButton);
    
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does not auto-dismiss when duration is 0', async () => {
    jest.useFakeTimers();
    const onClose = jest.fn();
    
    render(
      <Toast
        message="No auto dismiss"
        isVisible={true}
        onClose={onClose}
        duration={0}
      />
    );

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(onClose).not.toHaveBeenCalled();
    
    jest.useRealTimers();
  });

  it('does not render when isVisible is false', () => {
    const onClose = jest.fn();
    
    render(
      <Toast
        message="Hidden toast"
        isVisible={false}
        onClose={onClose}
      />
    );

    expect(screen.queryByText('Hidden toast')).not.toBeInTheDocument();
  });
});

describe('useToast', () => {
  it('shows and hides toast', () => {
    const { result } = renderHook(() => useToast());

    expect(result.current.toast.isVisible).toBe(false);

    act(() => {
      result.current.showToast('Test message', 'success');
    });

    expect(result.current.toast.isVisible).toBe(true);
    expect(result.current.toast.message).toBe('Test message');
    expect(result.current.toast.type).toBe('success');

    act(() => {
      result.current.hideToast();
    });

    expect(result.current.toast.isVisible).toBe(false);
  });
});
