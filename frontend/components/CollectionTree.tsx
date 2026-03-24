'use client';

import { Collection } from '@/types';
import { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, FolderOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CollectionTreeProps {
  collections: Collection[];
  onCollectionClick?: (collection: Collection) => void;
  selectedCollectionId?: number;
}

interface CollectionTreeNodeProps {
  collection: Collection;
  children: Collection[];
  onCollectionClick?: (collection: Collection) => void;
  selectedCollectionId?: number;
  level: number;
}

function CollectionTreeNode({ 
  collection, 
  children, 
  onCollectionClick,
  selectedCollectionId,
  level 
}: CollectionTreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = children.length > 0;
  const isSelected = selectedCollectionId === collection.id;

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  const handleClick = () => {
    onCollectionClick?.(collection);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    } else if (e.key === 'ArrowRight' && hasChildren && !isExpanded) {
      e.preventDefault();
      setIsExpanded(true);
    } else if (e.key === 'ArrowLeft' && hasChildren && isExpanded) {
      e.preventDefault();
      setIsExpanded(false);
    }
  };

  const paddingClass = level === 0 ? 'pl-3' : level === 1 ? 'pl-9' : level === 2 ? 'pl-[4.5rem]' : 'pl-[6rem]';

  return (
    <div className="select-none">
      <div
        className={`
          flex items-center gap-2 py-2 rounded cursor-pointer
          transition-colors duration-100
          ${paddingClass}
          ${isSelected 
            ? 'bg-primary text-primary-foreground font-black' 
            : 'hover:bg-muted font-bold'
          }
        `}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
        {...(hasChildren ? { 'aria-expanded': isExpanded } : {})}
        aria-label={`Collection: ${collection.name}`}
      >
        {hasChildren ? (
          <span
            onClick={handleToggle}
            className="flex-shrink-0 p-0.5 hover:bg-border/50 rounded cursor-pointer"
            aria-hidden="true"
          >
            {isExpanded ? (
              <ChevronDown size={16} strokeWidth={3} />
            ) : (
              <ChevronRight size={16} strokeWidth={3} />
            )}
          </span>
        ) : (
          <span className="w-5" />
        )}
        
        {isExpanded && hasChildren ? (
          <FolderOpen size={18} strokeWidth={2.5} className="flex-shrink-0" />
        ) : (
          <Folder size={18} strokeWidth={2.5} className="flex-shrink-0" />
        )}
        
        <span className="truncate uppercase tracking-wide text-sm">
          {collection.name}
        </span>
        
        <span className="ml-auto text-xs opacity-70">
          {collection.recipe_count || 0}
        </span>
      </div>

      <AnimatePresence>
        {isExpanded && hasChildren && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {children.map(child => {
              const grandchildren = collections.filter(
                c => c.parent_collection_id === child.id
              );
              return (
                <CollectionTreeNode
                  key={child.id}
                  collection={child}
                  children={grandchildren}
                  onCollectionClick={onCollectionClick}
                  selectedCollectionId={selectedCollectionId}
                  level={level + 1}
                />
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function CollectionTree({ 
  collections, 
  onCollectionClick,
  selectedCollectionId 
}: CollectionTreeProps) {
  // Build tree structure - get root collections (no parent)
  const rootCollections = collections.filter(c => !c.parent_collection_id);

  if (collections.length === 0) {
    return (
      <div className="text-center py-8 comic-panel">
        <div className="text-4xl mb-2">📁</div>
        <p className="text-muted-foreground font-bold text-sm">No collections yet</p>
      </div>
    );
  }

  return (
    <div className="comic-panel p-4 space-y-1">
      {rootCollections.map(collection => {
        const children = collections.filter(
          c => c.parent_collection_id === collection.id
        );
        return (
          <CollectionTreeNode
            key={collection.id}
            collection={collection}
            children={children}
            onCollectionClick={onCollectionClick}
            selectedCollectionId={selectedCollectionId}
            level={0}
          />
        );
      })}
    </div>
  );
}
