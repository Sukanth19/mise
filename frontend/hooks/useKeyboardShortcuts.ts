'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from '@/contexts/ThemeContext';

interface KeyboardShortcutsOptions {
  onShowHelp?: () => void;
}

/**
 * Custom hook for handling keyboard shortcuts
 * Supports:
 * - Ctrl/Cmd+N: Create new recipe
 * - Ctrl/Cmd+K: Focus search
 * - Ctrl/Cmd+T: Toggle theme
 * - ?: Show keyboard shortcuts help
 */
export function useKeyboardShortcuts(options?: KeyboardShortcutsOptions) {
  const router = useRouter();
  const themeContext = useTheme();
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const showHelp = useCallback(() => {
    setIsHelpOpen(true);
    options?.onShowHelp?.();
  }, [options]);

  const hideHelp = useCallback(() => {
    setIsHelpOpen(false);
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check for modifier key (Ctrl on Windows/Linux, Cmd on Mac)
      const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modifierKey = isMac ? event.metaKey : event.ctrlKey;

      // Ctrl/Cmd+N: Create new recipe
      if (modifierKey && event.key.toLowerCase() === 'n') {
        event.preventDefault();
        router.push('/recipes/new');
        return;
      }

      // Ctrl/Cmd+K: Focus search
      if (modifierKey && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        // Find search input and focus it
        const searchInput = document.querySelector('input[type="text"][placeholder*="Search"]') as HTMLInputElement;
        if (searchInput) {
          searchInput.focus();
          searchInput.select();
        }
        return;
      }

      // Ctrl/Cmd+T: Toggle theme
      if (modifierKey && event.key.toLowerCase() === 't') {
        event.preventDefault();
        if (themeContext) {
          themeContext.toggleTheme();
        }
        return;
      }

      // ?: Show help modal
      if (event.key === '?' && !event.ctrlKey && !event.metaKey && !event.altKey) {
        // Only trigger if not in an input field
        const target = event.target as HTMLElement;
        const isInputField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable;
        
        if (!isInputField) {
          event.preventDefault();
          showHelp();
        }
        return;
      }

      // Escape: Close help modal
      if (event.key === 'Escape' && isHelpOpen) {
        event.preventDefault();
        hideHelp();
        return;
      }
    };

    // Add event listener
    window.addEventListener('keydown', handleKeyDown);

    // Cleanup on unmount
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [router, themeContext, isHelpOpen, showHelp, hideHelp]);

  return {
    isHelpOpen,
    showHelp,
    hideHelp,
  };
}
