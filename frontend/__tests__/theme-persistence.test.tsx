import { render, screen, waitFor, cleanup } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import * as fc from 'fast-check';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';

// Test component that uses the theme context
function TestComponent() {
  const themeContext = useTheme();
  
  if (!themeContext) {
    return <div>No theme context</div>;
  }

  return (
    <div>
      <div data-testid="current-theme">{themeContext.theme}</div>
      <button 
        data-testid="toggle-button" 
        onClick={themeContext.toggleTheme}
      >
        Toggle
      </button>
    </div>
  );
}

describe('Theme Persistence Property Tests', () => {
  const localStorageMock: { [key: string]: string } = {};

  beforeEach(() => {
    // Clear the mock object
    Object.keys(localStorageMock).forEach(key => delete localStorageMock[key]);
    
    // Mock localStorage
    Object.defineProperty(global, 'localStorage', {
      value: {
        getItem: (key: string) => {
          return localStorageMock[key] || null;
        },
        setItem: (key: string, value: string) => {
          localStorageMock[key] = value;
        },
        removeItem: (key: string) => {
          delete localStorageMock[key];
        },
        clear: () => {
          Object.keys(localStorageMock).forEach(key => delete localStorageMock[key]);
        },
        length: Object.keys(localStorageMock).length,
        key: (index: number) => Object.keys(localStorageMock)[index] || null,
      },
      writable: true,
      configurable: true,
    });

    // Mock matchMedia - default to light mode
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      configurable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: false, // prefers-color-scheme: dark is false
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });
  });

  afterEach(() => {
    cleanup();
    jest.clearAllMocks();
  });

  /**
   * Property 1: Theme persistence round trip
   * **Validates: Requirements 1.3, 1.4**
   * 
   * Property: For any sequence of theme toggles, the final theme state
   * should be persisted to localStorage and restored on remount.
   */
  test('Property 1: Theme persistence round trip', async () => {
    await fc.assert(
      fc.asyncProperty(
        // Generate a sequence of toggle operations (1-10 toggles)
        fc.array(fc.constant('toggle'), { minLength: 1, maxLength: 10 }),
        async (toggleSequence) => {
          // Clear localStorage before each iteration
          Object.keys(localStorageMock).forEach(key => delete localStorageMock[key]);
          
          // First render: perform toggles
          let result = render(
            <ThemeProvider>
              <TestComponent />
            </ThemeProvider>
          );

          try {
            // Wait for initial mount and theme to be determined
            // The component will check localStorage (empty) then system preference (light)
            await waitFor(() => {
              const elements = result.container.querySelectorAll('[data-testid="current-theme"]');
              if (elements.length !== 1) {
                throw new Error(`Expected 1 element, found ${elements.length}`);
              }
              // After mount, should be 'light' based on system preference
              expect(elements[0]).toHaveTextContent('light');
            }, { timeout: 3000 });

            // Get initial theme after mount
            const initialTheme = result.container.querySelector('[data-testid="current-theme"]')?.textContent as 'light' | 'dark';
            
            // Calculate expected final theme based on number of toggles from initial state
            const expectedTheme = toggleSequence.length % 2 === 0 ? initialTheme : (initialTheme === 'light' ? 'dark' : 'light');

            // Perform all toggles
            const toggleButton = result.container.querySelector('[data-testid="toggle-button"]') as HTMLElement;
            for (let i = 0; i < toggleSequence.length; i++) {
              await act(async () => {
                toggleButton.click();
              });
            }

            // Wait for final state
            await waitFor(() => {
              const element = result.container.querySelector('[data-testid="current-theme"]');
              expect(element).toHaveTextContent(expectedTheme);
            }, { timeout: 2000 });

            // Verify localStorage was updated (wait longer for the effect to run)
            await waitFor(() => {
              expect(localStorageMock['theme']).toBe(expectedTheme);
            }, { timeout: 3000 });

            // Unmount component
            result.unmount();
            
            // Ensure cleanup
            await act(async () => {
              await new Promise(resolve => setTimeout(resolve, 50));
            });

            // Second render: verify persistence
            result = render(
              <ThemeProvider>
                <TestComponent />
              </ThemeProvider>
            );

            // Wait for mount and theme restoration
            await waitFor(() => {
              const elements = result.container.querySelectorAll('[data-testid="current-theme"]');
              if (elements.length !== 1) {
                throw new Error(`Expected 1 element, found ${elements.length}`);
              }
              expect(elements[0]).toHaveTextContent(expectedTheme);
            }, { timeout: 3000 });
          } finally {
            // Always cleanup
            result.unmount();
            cleanup();
          }
        }
      ),
      { numRuns: 20 } // Run 20 test cases
    );
  });

  /**
   * Unit test: Verify theme is applied to document element
   */
  test('Theme is applied to document element', async () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('current-theme')).toBeInTheDocument();
    });

    // Check initial theme
    const initialTheme = screen.getByTestId('current-theme').textContent;
    expect(document.documentElement.getAttribute('data-theme')).toBe(initialTheme);

    // Toggle theme
    const toggleButton = screen.getByTestId('toggle-button');
    await act(async () => {
      toggleButton.click();
    });

    // Wait for theme change
    await waitFor(() => {
      const newTheme = screen.getByTestId('current-theme').textContent;
      expect(document.documentElement.getAttribute('data-theme')).toBe(newTheme);
    });
  });

  /**
   * Unit test: Verify theme defaults to system preference when no saved theme
   */
  test('Theme defaults to system preference when no saved theme', async () => {
    // Clear localStorage
    Object.keys(localStorageMock).forEach(key => delete localStorageMock[key]);
    
    // Mock system preference for light mode (matches: false for dark mode query)
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: false, // prefers-color-scheme: dark is false, so light mode
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('current-theme')).toHaveTextContent('light');
    });
  });

  /**
   * Unit test: Verify saved theme overrides system preference
   */
  test('Saved theme overrides system preference', async () => {
    // Set saved theme to light
    localStorageMock['theme'] = 'light';

    // Mock system preference for dark mode
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Should use saved theme (light) instead of system preference (dark)
    await waitFor(() => {
      expect(screen.getByTestId('current-theme')).toHaveTextContent('light');
    });
  });
});
