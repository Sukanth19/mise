import { renderHook, act } from '@testing-library/react';
import { useKeyboardShortcuts } from './useKeyboardShortcuts';
import { useRouter } from 'next/navigation';
import { useTheme } from '@/contexts/ThemeContext';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock ThemeContext
jest.mock('@/contexts/ThemeContext', () => ({
  useTheme: jest.fn(),
}));

describe('useKeyboardShortcuts', () => {
  let mockPush: jest.Mock;
  let mockToggleTheme: jest.Mock;

  beforeEach(() => {
    mockPush = jest.fn();
    mockToggleTheme = jest.fn();

    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });

    (useTheme as jest.Mock).mockReturnValue({
      theme: 'dark',
      toggleTheme: mockToggleTheme,
      prefersReducedMotion: false,
    });

    // Mock navigator.platform for Mac detection
    Object.defineProperty(navigator, 'platform', {
      value: 'Win32',
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Ctrl+N shortcut', () => {
    it('navigates to new recipe page on Ctrl+N (Windows/Linux)', () => {
      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 'n',
        ctrlKey: true,
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(mockPush).toHaveBeenCalledWith('/recipes/new');
    });

    it('navigates to new recipe page on Cmd+N (Mac)', () => {
      Object.defineProperty(navigator, 'platform', {
        value: 'MacIntel',
        writable: true,
        configurable: true,
      });

      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 'n',
        metaKey: true,
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(mockPush).toHaveBeenCalledWith('/recipes/new');
    });

    it('handles uppercase N key', () => {
      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 'N',
        ctrlKey: true,
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(mockPush).toHaveBeenCalledWith('/recipes/new');
    });
  });

  describe('Ctrl+K shortcut', () => {
    it('focuses search input on Ctrl+K', () => {
      renderHook(() => useKeyboardShortcuts());

      // Create a mock search input
      const searchInput = document.createElement('input');
      searchInput.type = 'text';
      searchInput.placeholder = 'Search recipes...';
      searchInput.focus = jest.fn();
      searchInput.select = jest.fn();
      document.body.appendChild(searchInput);

      const event = new KeyboardEvent('keydown', {
        key: 'k',
        ctrlKey: true,
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(searchInput.focus).toHaveBeenCalled();
      expect(searchInput.select).toHaveBeenCalled();

      document.body.removeChild(searchInput);
    });

    it('does nothing if search input is not found', () => {
      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 'k',
        ctrlKey: true,
        bubbles: true,
      });

      // Should not throw error
      expect(() => {
        act(() => {
          window.dispatchEvent(event);
        });
      }).not.toThrow();
    });
  });

  describe('Ctrl+T shortcut', () => {
    it('toggles theme on Ctrl+T', () => {
      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 't',
        ctrlKey: true,
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(mockToggleTheme).toHaveBeenCalled();
    });

    it('does nothing if theme context is null', () => {
      (useTheme as jest.Mock).mockReturnValue(null);

      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 't',
        ctrlKey: true,
        bubbles: true,
      });

      // Should not throw error
      expect(() => {
        act(() => {
          window.dispatchEvent(event);
        });
      }).not.toThrow();
    });
  });

  describe('? shortcut', () => {
    it('shows help modal on ? key press', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      expect(result.current.isHelpOpen).toBe(false);

      const event = new KeyboardEvent('keydown', {
        key: '?',
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(result.current.isHelpOpen).toBe(true);
    });

    it('does not show help when ? is pressed in input field', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      const input = document.createElement('input');
      document.body.appendChild(input);

      const event = new KeyboardEvent('keydown', {
        key: '?',
        bubbles: true,
      });
      Object.defineProperty(event, 'target', { value: input, writable: false });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(result.current.isHelpOpen).toBe(false);

      document.body.removeChild(input);
    });

    it('does not show help when ? is pressed in textarea', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      const textarea = document.createElement('textarea');
      document.body.appendChild(textarea);

      const event = new KeyboardEvent('keydown', {
        key: '?',
        bubbles: true,
      });
      Object.defineProperty(event, 'target', { value: textarea, writable: false });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(result.current.isHelpOpen).toBe(false);

      document.body.removeChild(textarea);
    });

    it('calls onShowHelp callback when provided', () => {
      const onShowHelp = jest.fn();
      const { result } = renderHook(() => useKeyboardShortcuts({ onShowHelp }));

      const event = new KeyboardEvent('keydown', {
        key: '?',
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(onShowHelp).toHaveBeenCalled();
      expect(result.current.isHelpOpen).toBe(true);
    });
  });

  describe('Escape key', () => {
    it('closes help modal on Escape key', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      // Open help modal first
      act(() => {
        result.current.showHelp();
      });

      expect(result.current.isHelpOpen).toBe(true);

      // Press Escape
      const event = new KeyboardEvent('keydown', {
        key: 'Escape',
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(result.current.isHelpOpen).toBe(false);
    });

    it('does nothing if help modal is not open', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      expect(result.current.isHelpOpen).toBe(false);

      const event = new KeyboardEvent('keydown', {
        key: 'Escape',
        bubbles: true,
      });

      // Should not throw error
      expect(() => {
        act(() => {
          window.dispatchEvent(event);
        });
      }).not.toThrow();
    });
  });

  describe('showHelp and hideHelp methods', () => {
    it('provides showHelp method to manually open help', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      expect(result.current.isHelpOpen).toBe(false);

      act(() => {
        result.current.showHelp();
      });

      expect(result.current.isHelpOpen).toBe(true);
    });

    it('provides hideHelp method to manually close help', () => {
      const { result } = renderHook(() => useKeyboardShortcuts());

      act(() => {
        result.current.showHelp();
      });

      expect(result.current.isHelpOpen).toBe(true);

      act(() => {
        result.current.hideHelp();
      });

      expect(result.current.isHelpOpen).toBe(false);
    });
  });

  describe('cleanup', () => {
    it('removes event listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener');

      const { unmount } = renderHook(() => useKeyboardShortcuts());

      unmount();

      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

      removeEventListenerSpy.mockRestore();
    });
  });

  describe('modifier key detection', () => {
    it('does not trigger shortcuts without modifier key', () => {
      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 'n',
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(mockPush).not.toHaveBeenCalled();
    });

    it('does not trigger shortcuts with wrong modifier key on Mac', () => {
      Object.defineProperty(navigator, 'platform', {
        value: 'MacIntel',
        writable: true,
        configurable: true,
      });

      renderHook(() => useKeyboardShortcuts());

      const event = new KeyboardEvent('keydown', {
        key: 'n',
        ctrlKey: true, // Should be metaKey on Mac
        bubbles: true,
      });

      act(() => {
        window.dispatchEvent(event);
      });

      expect(mockPush).not.toHaveBeenCalled();
    });
  });
});
