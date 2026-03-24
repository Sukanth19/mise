'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

interface RatingStarsProps {
  value: number; // 0-5, supports decimals for display
  onChange?: (rating: number) => void;
  readOnly?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function RatingStars({ 
  value, 
  onChange, 
  readOnly = false,
  size = 'md' 
}: RatingStarsProps) {
  const [hoverRating, setHoverRating] = useState<number | null>(null);

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const handleClick = (rating: number) => {
    if (!readOnly && onChange) {
      onChange(rating);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, rating: number) => {
    if (readOnly) return;
    
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick(rating);
    }
  };

  const getStarFill = (starIndex: number): number => {
    const displayValue = hoverRating !== null ? hoverRating : value;
    
    if (displayValue >= starIndex) {
      return 1; // Full star
    } else if (displayValue > starIndex - 1) {
      return displayValue - (starIndex - 1); // Partial star
    }
    return 0; // Empty star
  };

  return (
    <div 
      className="flex items-center gap-1"
      role="group"
      aria-label={`Rating: ${value} out of 5 stars`}
    >
      {[1, 2, 3, 4, 5].map((starIndex) => {
        const fillPercentage = getStarFill(starIndex);
        const isHovered = hoverRating !== null && starIndex <= hoverRating;
        
        return (
          <button
            key={starIndex}
            type="button"
            disabled={readOnly}
            onClick={() => handleClick(starIndex)}
            onMouseEnter={() => !readOnly && setHoverRating(starIndex)}
            onMouseLeave={() => !readOnly && setHoverRating(null)}
            onKeyDown={(e) => handleKeyDown(e, starIndex)}
            className={`relative ${sizeClasses[size]} ${
              readOnly ? 'cursor-default' : 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded'
            } ${!readOnly ? 'transition-transform hover:scale-110 active:scale-95' : ''}`}
            aria-label={`${starIndex} star${starIndex > 1 ? 's' : ''}`}
            tabIndex={readOnly ? -1 : 0}
          >
            {/* Background (empty) star */}
            <svg
              className="absolute inset-0 text-muted-foreground/30"
              fill="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            
            {/* Filled star with gradient for partial fills */}
            <svg
              className={`absolute inset-0 ${
                isHovered || fillPercentage > 0 ? 'text-warning' : 'text-transparent'
              } transition-colors duration-150`}
              fill="url(#star-gradient)"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient id={`star-gradient-${starIndex}`}>
                  <stop offset={`${fillPercentage * 100}%`} stopColor="currentColor" />
                  <stop offset={`${fillPercentage * 100}%`} stopColor="transparent" />
                </linearGradient>
              </defs>
              <path 
                fill={`url(#star-gradient-${starIndex})`}
                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" 
              />
            </svg>
            
            {/* Comic-style border */}
            <svg
              className="absolute inset-0 text-border pointer-events-none"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
          </button>
        );
      })}
      
      {/* Display numeric value for screen readers */}
      <span className="sr-only">{value} out of 5 stars</span>
    </div>
  );
}
