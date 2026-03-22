'use client';

import Header from '@/components/Header';
import PageTransition from '@/components/PageTransition';

export default function LayoutWrapper({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <PageTransition>{children}</PageTransition>
    </>
  );
}
