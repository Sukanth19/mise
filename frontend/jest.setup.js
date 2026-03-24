import '@testing-library/jest-dom'

// Mock framer-motion to avoid jsx-runtime issues
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => {
      const { initial, animate, transition, whileHover, whileTap, exit, ...rest } = props;
      return <div {...rest}>{children}</div>;
    },
    button: ({ children, ...props }) => {
      const { initial, animate, transition, whileHover, whileTap, exit, ...rest } = props;
      return <button {...rest}>{children}</button>;
    },
  },
  AnimatePresence: ({ children }) => children,
}))

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Pencil: () => <svg data-testid="pencil-icon" />,
  Trash2: () => <svg data-testid="trash2-icon" />,
  Folder: () => <svg data-testid="folder-icon" />,
  FolderOpen: () => <svg data-testid="folder-open-icon" />,
  FolderPlus: () => <svg data-testid="folder-plus-icon" />,
  ChevronRight: () => <svg data-testid="chevron-right-icon" />,
  ChevronDown: () => <svg data-testid="chevron-down-icon" />,
  X: () => <svg data-testid="x-icon" />,
  Check: () => <svg data-testid="check-icon" />,
  Plus: () => <svg data-testid="plus-icon" />,
  Share2: () => <svg data-testid="share2-icon" />,
  ArrowLeft: () => <svg data-testid="arrow-left-icon" />,
}))
