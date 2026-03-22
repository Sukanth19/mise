import '@testing-library/jest-dom'

// Mock framer-motion to avoid jsx-runtime issues
jest.mock('framer-motion', () => ({
  motion: {
    div: 'div',
    button: 'button',
  },
  AnimatePresence: ({ children }) => children,
}))
