import { render, screen, fireEvent } from '@testing-library/react';
import EmptyState from './EmptyState';

describe('EmptyState', () => {
  it('renders icon, message, and description', () => {
    render(
      <EmptyState
        icon="📝"
        message="No recipes found"
        description="Start by creating your first recipe"
      />
    );

    expect(screen.getByText('📝')).toBeInTheDocument();
    expect(screen.getByText('No recipes found')).toBeInTheDocument();
    expect(screen.getByText('Start by creating your first recipe')).toBeInTheDocument();
  });

  it('renders without description', () => {
    render(
      <EmptyState
        icon="📝"
        message="No recipes found"
      />
    );

    expect(screen.getByText('📝')).toBeInTheDocument();
    expect(screen.getByText('No recipes found')).toBeInTheDocument();
  });

  it('renders action button when provided', () => {
    const handleClick = jest.fn();
    
    render(
      <EmptyState
        icon="📝"
        message="No recipes found"
        action={{
          label: 'Create Recipe',
          onClick: handleClick,
        }}
      />
    );

    const button = screen.getByRole('button', { name: 'Create Recipe' });
    expect(button).toBeInTheDocument();
    
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not render action button when not provided', () => {
    render(
      <EmptyState
        icon="📝"
        message="No recipes found"
      />
    );

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('applies correct styling classes', () => {
    const { container } = render(
      <EmptyState
        icon="📝"
        message="No recipes found"
      />
    );

    const heading = screen.getByText('No recipes found');
    expect(heading).toHaveClass('comic-heading');
  });
});
