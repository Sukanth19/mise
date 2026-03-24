import { render, screen, fireEvent } from '@testing-library/react';
import RatingStars from './RatingStars';

describe('RatingStars Unit Tests', () => {
  describe('Rendering', () => {
    test('renders 5 stars', () => {
      const { container } = render(<RatingStars value={0} />);
      const stars = container.querySelectorAll('button');
      expect(stars).toHaveLength(5);
    });

    test('renders with value 0 (no stars filled)', () => {
      render(<RatingStars value={0} />);
      expect(screen.getByLabelText('Rating: 0 out of 5 stars')).toBeInTheDocument();
    });

    test('renders with value 3 (3 stars filled)', () => {
      render(<RatingStars value={3} />);
      expect(screen.getByLabelText('Rating: 3 out of 5 stars')).toBeInTheDocument();
    });

    test('renders with value 5 (all stars filled)', () => {
      render(<RatingStars value={5} />);
      expect(screen.getByLabelText('Rating: 5 out of 5 stars')).toBeInTheDocument();
    });

    test('renders with decimal value 2.5 (half stars)', () => {
      render(<RatingStars value={2.5} />);
      expect(screen.getByLabelText('Rating: 2.5 out of 5 stars')).toBeInTheDocument();
    });

    test('renders with decimal value 3.7', () => {
      render(<RatingStars value={3.7} />);
      expect(screen.getByLabelText('Rating: 3.7 out of 5 stars')).toBeInTheDocument();
    });
  });

  describe('Interactive Mode', () => {
    test('calls onChange with correct value when star is clicked', () => {
      const handleChange = jest.fn();
      const { container } = render(<RatingStars value={0} onChange={handleChange} />);
      
      const stars = container.querySelectorAll('button');
      fireEvent.click(stars[2]); // Click 3rd star
      
      expect(handleChange).toHaveBeenCalledWith(3);
    });

    test('calls onChange when clicking different stars', () => {
      const handleChange = jest.fn();
      const { container } = render(<RatingStars value={0} onChange={handleChange} />);
      
      const stars = container.querySelectorAll('button');
      
      fireEvent.click(stars[0]); // 1 star
      expect(handleChange).toHaveBeenCalledWith(1);
      
      fireEvent.click(stars[4]); // 5 stars
      expect(handleChange).toHaveBeenCalledWith(5);
    });

    test('updates rating when clicking on a star', () => {
      const handleChange = jest.fn();
      const { container } = render(<RatingStars value={2} onChange={handleChange} />);
      
      const stars = container.querySelectorAll('button');
      fireEvent.click(stars[3]); // Click 4th star
      
      expect(handleChange).toHaveBeenCalledWith(4);
    });

    test('stars are not disabled in interactive mode', () => {
      const { container } = render(<RatingStars value={0} onChange={() => {}} />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star).not.toBeDisabled();
      });
    });

    test('stars have cursor-pointer class in interactive mode', () => {
      const { container } = render(<RatingStars value={0} onChange={() => {}} />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star.className).toContain('cursor-pointer');
      });
    });
  });

  describe('Read-Only Mode', () => {
    test('does not call onChange when star is clicked in read-only mode', () => {
      const handleChange = jest.fn();
      const { container } = render(
        <RatingStars value={3} onChange={handleChange} readOnly={true} />
      );
      
      const stars = container.querySelectorAll('button');
      fireEvent.click(stars[4]);
      
      expect(handleChange).not.toHaveBeenCalled();
    });

    test('stars are disabled in read-only mode', () => {
      const { container } = render(<RatingStars value={3} readOnly={true} />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star).toBeDisabled();
      });
    });

    test('stars have cursor-default class in read-only mode', () => {
      const { container } = render(<RatingStars value={3} readOnly={true} />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star.className).toContain('cursor-default');
      });
    });

    test('stars have tabIndex -1 in read-only mode', () => {
      const { container } = render(<RatingStars value={3} readOnly={true} />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star).toHaveAttribute('tabIndex', '-1');
      });
    });
  });

  describe('Keyboard Navigation', () => {
    test('calls onChange when Enter key is pressed', () => {
      const handleChange = jest.fn();
      const { container } = render(<RatingStars value={0} onChange={handleChange} />);
      
      const stars = container.querySelectorAll('button');
      fireEvent.keyDown(stars[2], { key: 'Enter' });
      
      expect(handleChange).toHaveBeenCalledWith(3);
    });

    test('calls onChange when Space key is pressed', () => {
      const handleChange = jest.fn();
      const { container } = render(<RatingStars value={0} onChange={handleChange} />);
      
      const stars = container.querySelectorAll('button');
      fireEvent.keyDown(stars[1], { key: ' ' });
      
      expect(handleChange).toHaveBeenCalledWith(2);
    });

    test('does not call onChange for other keys', () => {
      const handleChange = jest.fn();
      const { container } = render(<RatingStars value={0} onChange={handleChange} />);
      
      const stars = container.querySelectorAll('button');
      fireEvent.keyDown(stars[2], { key: 'a' });
      fireEvent.keyDown(stars[2], { key: 'Escape' });
      
      expect(handleChange).not.toHaveBeenCalled();
    });

    test('does not respond to keyboard in read-only mode', () => {
      const handleChange = jest.fn();
      const { container } = render(
        <RatingStars value={3} onChange={handleChange} readOnly={true} />
      );
      
      const stars = container.querySelectorAll('button');
      fireEvent.keyDown(stars[2], { key: 'Enter' });
      fireEvent.keyDown(stars[2], { key: ' ' });
      
      expect(handleChange).not.toHaveBeenCalled();
    });

    test('stars have tabIndex 0 in interactive mode for keyboard navigation', () => {
      const { container } = render(<RatingStars value={0} onChange={() => {}} />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star).toHaveAttribute('tabIndex', '0');
      });
    });
  });

  describe('Accessibility', () => {
    test('has role="group" on container', () => {
      const { container } = render(<RatingStars value={3} />);
      const group = container.querySelector('[role="group"]');
      expect(group).toBeInTheDocument();
    });

    test('has aria-label on container with rating value', () => {
      render(<RatingStars value={3.5} />);
      expect(screen.getByLabelText('Rating: 3.5 out of 5 stars')).toBeInTheDocument();
    });

    test('each star has aria-label', () => {
      render(<RatingStars value={0} onChange={() => {}} />);
      
      expect(screen.getByLabelText('1 star')).toBeInTheDocument();
      expect(screen.getByLabelText('2 stars')).toBeInTheDocument();
      expect(screen.getByLabelText('3 stars')).toBeInTheDocument();
      expect(screen.getByLabelText('4 stars')).toBeInTheDocument();
      expect(screen.getByLabelText('5 stars')).toBeInTheDocument();
    });

    test('has screen reader text with numeric value', () => {
      render(<RatingStars value={4} />);
      const srText = screen.getByText('4 out of 5 stars');
      expect(srText).toHaveClass('sr-only');
    });
  });

  describe('Size Variants', () => {
    test('renders with small size', () => {
      const { container } = render(<RatingStars value={3} size="sm" />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star.className).toContain('w-4');
        expect(star.className).toContain('h-4');
      });
    });

    test('renders with medium size (default)', () => {
      const { container } = render(<RatingStars value={3} />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star.className).toContain('w-6');
        expect(star.className).toContain('h-6');
      });
    });

    test('renders with large size', () => {
      const { container } = render(<RatingStars value={3} size="lg" />);
      const stars = container.querySelectorAll('button');
      
      stars.forEach(star => {
        expect(star.className).toContain('w-8');
        expect(star.className).toContain('h-8');
      });
    });
  });

  describe('Edge Cases', () => {
    test('handles value greater than 5', () => {
      render(<RatingStars value={10} />);
      expect(screen.getByLabelText('Rating: 10 out of 5 stars')).toBeInTheDocument();
    });

    test('handles negative value', () => {
      render(<RatingStars value={-1} />);
      expect(screen.getByLabelText('Rating: -1 out of 5 stars')).toBeInTheDocument();
    });

    test('works without onChange prop', () => {
      const { container } = render(<RatingStars value={3} />);
      const stars = container.querySelectorAll('button');
      
      // Should not throw error when clicking
      expect(() => fireEvent.click(stars[2])).not.toThrow();
    });
  });
});
