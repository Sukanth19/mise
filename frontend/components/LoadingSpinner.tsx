'use client';

import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  variant?: 'default' | 'recipe' | 'collection' | 'minimal';
}

export default function LoadingSpinner({ 
  size = 'md', 
  text,
  variant = 'default' 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-16 h-16',
    lg: 'w-24 h-24',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-xl',
  };

  if (variant === 'minimal') {
    return (
      <div className="flex items-center justify-center gap-2">
        <motion.div
          className={`${sizeClasses[size]} border-4 border-muted border-t-primary rounded-full`}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
        {text && (
          <span className={`${textSizeClasses[size]} font-bold text-muted-foreground`}>
            {text}
          </span>
        )}
      </div>
    );
  }

  if (variant === 'recipe') {
    return (
      <div className="flex flex-col items-center justify-center gap-4">
        {/* Cooking pot animation */}
        <motion.div className="relative">
          <motion.div
            className={`${sizeClasses[size]} relative`}
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
          >
            <svg viewBox="0 0 100 100" className="w-full h-full" fill="hsl(var(--primary))">
              <rect x="20" y="40" width="60" height="40" rx="5" />
              <rect x="15" y="35" width="70" height="8" rx="4" />
              <path d="M30 35 L30 25 L35 25" stroke="hsl(var(--primary))" strokeWidth="3" fill="none" />
              <path d="M70 35 L70 25 L65 25" stroke="hsl(var(--primary))" strokeWidth="3" fill="none" />
            </svg>
          </motion.div>
          
          {/* Steam bubbles */}
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-3 h-3 bg-accent rounded-full opacity-60"
              style={{ left: `${30 + i * 20}%`, bottom: '100%' }}
              animate={{
                y: [-20, -60],
                opacity: [0.6, 0],
                scale: [1, 0.5],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.4,
              }}
            />
          ))}
        </motion.div>
        
        {text && (
          <motion.span
            className={`${textSizeClasses[size]} comic-text text-foreground`}
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {text}
          </motion.span>
        )}
      </div>
    );
  }

  if (variant === 'collection') {
    return (
      <div className="flex flex-col items-center justify-center gap-4">
        {/* Book/folder animation */}
        <motion.div className="relative">
          <motion.div
            className={`${sizeClasses[size]}`}
            animate={{ rotateY: [0, 180, 360] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            style={{ transformStyle: 'preserve-3d' }}
          >
            <svg viewBox="0 0 100 100" className="w-full h-full" fill="hsl(var(--secondary))">
              <rect x="20" y="25" width="60" height="50" rx="3" />
              <rect x="25" y="30" width="50" height="40" rx="2" fill="hsl(var(--card))" />
              <line x1="30" y1="40" x2="70" y2="40" stroke="hsl(var(--muted))" strokeWidth="2" />
              <line x1="30" y1="50" x2="70" y2="50" stroke="hsl(var(--muted))" strokeWidth="2" />
              <line x1="30" y1="60" x2="60" y2="60" stroke="hsl(var(--muted))" strokeWidth="2" />
            </svg>
          </motion.div>
        </motion.div>
        
        {text && (
          <motion.span
            className={`${textSizeClasses[size]} comic-text text-foreground`}
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {text}
          </motion.span>
        )}
      </div>
    );
  }

  // Default variant - spinning utensils
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className="relative">
        {/* Rotating utensils */}
        <motion.div
          className={`${sizeClasses[size]} relative`}
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <svg viewBox="0 0 100 100" className="w-full h-full">
            {/* Fork */}
            <g fill="hsl(var(--primary))">
              <rect x="45" y="20" width="3" height="60" />
              <rect x="40" y="20" width="3" height="25" />
              <rect x="50" y="20" width="3" height="25" />
            </g>
            {/* Spoon */}
            <g fill="hsl(var(--accent))" transform="rotate(90 50 50)">
              <rect x="45" y="30" width="3" height="50" />
              <circle cx="46.5" cy="25" r="8" />
            </g>
          </svg>
        </motion.div>

        {/* Orbiting dots */}
        {[...Array(4)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-accent rounded-full"
            style={{
              top: '50%',
              left: '50%',
              marginTop: '-4px',
              marginLeft: '-4px',
            }}
            animate={{
              x: [0, 40 * Math.cos((i * Math.PI) / 2), 0],
              y: [0, 40 * Math.sin((i * Math.PI) / 2), 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </div>

      {text && (
        <motion.span
          className={`${textSizeClasses[size]} comic-text text-foreground`}
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          {text}
        </motion.span>
      )}
    </div>
  );
}
