'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
  message: string;
  type?: ToastType;
  isVisible: boolean;
  onClose: () => void;
  duration?: number;
}

const toastIcons = {
  success: '✓',
  error: '✗',
  info: 'ℹ',
  warning: '⚠',
};

const toastStyles = {
  success: 'bg-success text-white',
  error: 'bg-destructive text-destructive-foreground',
  info: 'bg-secondary text-secondary-foreground',
  warning: 'bg-warning text-foreground',
};

export default function Toast({ 
  message, 
  type = 'info', 
  isVisible, 
  onClose, 
  duration = 3000 
}: ToastProps) {
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          transition={{ type: 'spring', duration: 0.4 }}
          className="fixed top-4 right-4 z-[100] max-w-md"
        >
          <div className={`comic-panel px-6 py-4 ${toastStyles[type]} flex items-center gap-3 shadow-lg`}>
            <span className="text-2xl font-black">{toastIcons[type]}</span>
            <p className="flex-1 font-bold">{message}</p>
            <button
              type="button"
              onClick={onClose}
              className="text-2xl font-black hover:opacity-70 transition-opacity"
              aria-label="Close notification"
            >
              ×
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function useToast() {
  const [toast, setToast] = useState<{
    message: string;
    type: ToastType;
    isVisible: boolean;
  }>({
    message: '',
    type: 'info',
    isVisible: false,
  });

  const showToast = (message: string, type: ToastType = 'info') => {
    setToast({ message, type, isVisible: true });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  return { toast, showToast, hideToast };
}

