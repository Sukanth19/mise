'use client';

import { motion } from 'framer-motion';

export default function LoginAnimation() {
  return (
    <div className="flex flex-col items-center justify-center gap-6">
      {/* Animated chef hat icon */}
      <motion.div
        className="relative"
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          className="relative w-24 h-24"
          animate={{
            rotate: [0, -10, 10, -10, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          {/* Chef hat */}
          <svg
            viewBox="0 0 100 100"
            className="w-full h-full"
            fill="hsl(var(--primary))"
          >
            <path d="M50 20 C30 20 20 30 20 45 L20 55 L80 55 L80 45 C80 30 70 20 50 20 Z" />
            <rect x="25" y="55" width="50" height="25" rx="5" />
            <circle cx="30" cy="35" r="8" opacity="0.3" />
            <circle cx="50" cy="30" r="10" opacity="0.3" />
            <circle cx="70" cy="35" r="8" opacity="0.3" />
          </svg>
        </motion.div>

        {/* Sparkle effects */}
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-accent rounded-full"
            style={{
              top: `${20 + i * 20}%`,
              left: `${-10 + i * 50}%`,
            }}
            animate={{
              scale: [0, 1, 0],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: i * 0.3,
            }}
          />
        ))}
      </motion.div>

      {/* Loading text */}
      <motion.div
        className="flex gap-2 items-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <span className="comic-heading text-xl text-foreground">
          LOGGING IN
        </span>
        <motion.span
          className="flex gap-1"
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <span className="text-xl font-black">.</span>
          <span className="text-xl font-black">.</span>
          <span className="text-xl font-black">.</span>
        </motion.span>
      </motion.div>

      {/* Progress bar */}
      <div className="w-64 h-3 comic-border rounded-none overflow-hidden bg-muted">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: "0%" }}
          animate={{ width: "100%" }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>
    </div>
  );
}
