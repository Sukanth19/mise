'use client';

import { Collection } from '@/types';
import CollectionCard from './CollectionCard';
import { motion, AnimatePresence } from 'framer-motion';

interface CollectionGridProps {
  collections: Collection[];
  onEdit?: (collection: Collection) => void;
  onDelete?: (collection: Collection) => void;
}

export default function CollectionGrid({ 
  collections, 
  onEdit, 
  onDelete 
}: CollectionGridProps) {
  if (collections.length === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12 comic-panel max-w-md mx-auto"
      >
        <div className="text-6xl mb-4">📁</div>
        <p className="text-muted-foreground font-bold text-lg">No collections found</p>
        <p className="text-muted-foreground text-sm mt-2">Create a collection to organize your recipes</p>
      </motion.div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <AnimatePresence mode="popLayout">
        {collections.map((collection, index) => (
          <CollectionCard 
            key={collection.id} 
            collection={collection} 
            index={index}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
