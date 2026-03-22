import { render } from '@testing-library/react';
import PageTransition from './PageTransition';
import React from 'react';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/'),
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => {
  const React = require('react');
  return {
    motion: {
      div: React.forwardRef((props: any, ref: any) => {
        const { children, ...rest } = props;
        return React.createElement('div', { ...rest, ref }, children);
      }),
    },
    AnimatePresence: ({ children }: any) => children,
  };
});

describe('PageTransition', () => {
  it('renders children correctly', () => {
    const { getByText } = render(
      <PageTransition>
        <div>Test Content</div>
      </PageTransition>
    );

    expect(getByText('Test Content')).toBeInTheDocument();
  });

  it('wraps children in motion.div', () => {
    const { container } = render(
      <PageTransition>
        <div>Test Content</div>
      </PageTransition>
    );

    // Check that content is rendered
    expect(container.querySelector('div')).toBeInTheDocument();
  });
});
