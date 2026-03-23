'use client';

import { motion, AnimatePresence } from 'framer-motion';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  isDeleting?: boolean;
}

export default function DeleteConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  isDeleting = false,
}: DeleteConfirmationModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop with fade animation */}
          <motion.div
            className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />

          {/* Modal with scale and fade animation */}
          <motion.div
            className="relative comic-panel max-w-md w-full p-6"
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ type: 'spring', duration: 0.4 }}
          >
            <div className="text-6xl text-center mb-4">💥</div>
            <h2 className="text-2xl comic-heading text-foreground mb-4 text-center">
              Delete Recipe?
            </h2>
            <p className="text-muted-foreground mb-6 font-bold text-center">
              Are you sure you want to delete "{title}"? This action cannot be undone.
            </p>

            <div className="flex gap-3 justify-center">
              <button
                type="button"
                onClick={onClose}
                disabled={isDeleting}
                className="comic-button px-6 py-3 bg-muted text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
              >
                CANCEL
              </button>
              <button
                type="button"
                onClick={onConfirm}
                disabled={isDeleting}
                className="comic-button px-6 py-3 bg-destructive text-destructive-foreground disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isDeleting ? 'DELETING...' : 'DELETE'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
