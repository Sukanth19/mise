'use client';

import Header from '@/components/Header';
import PageTransition from '@/components/PageTransition';
import KeyboardShortcutsHelp from '@/components/KeyboardShortcutsHelp';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

export default function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const { isHelpOpen, hideHelp } = useKeyboardShortcuts();

  return (
    <>
      <Header />
      <PageTransition>{children}</PageTransition>
      <KeyboardShortcutsHelp isOpen={isHelpOpen} onClose={hideHelp} />
    </>
  );
}
