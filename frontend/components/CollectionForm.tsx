'use client';

import React, { useState, FormEvent } from 'react';
import ImageUpload from './ImageUpload';
import { CollectionCreate, CollectionUpdate, Collection } from '@/types';

interface CollectionFormProps {
  initialData?: CollectionUpdate & { id?: number; nesting_level?: number };
  onSubmit: (data: CollectionCreate | CollectionUpdate) => Promise<void>;
  submitLabel?: string;
  availableCollections?: Collection[];
  currentCollectionId?: number;
}

export default function CollectionForm({ 
  initialData, 
  onSubmit, 
  submitLabel = 'Save Collection',
  availableCollections = [],
  currentCollectionId
}: CollectionFormProps) {
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [coverImageUrl, setCoverImageUrl] = useState(initialData?.cover_image_url || '');
  const [parentCollectionId, setParentCollectionId] = useState<number | undefined>(
    (initialData as any)?.parent_collection_id
  );
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleImageUploaded = (url: string) => {
    setCoverImageUrl(url);
  };

  const validateForm = (): boolean => {
    if (!name.trim()) {
      setError('Collection name is required');
      return false;
    }

    // Validate nesting level (max 3)
    if (parentCollectionId) {
      const parentCollection = availableCollections.find(c => c.id === parentCollectionId);
      if (parentCollection && parentCollection.nesting_level >= 2) {
        setError('Cannot nest more than 3 levels deep');
        return false;
      }
    }

    setError(null);
    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const collectionData: CollectionCreate = {
        name: name.trim(),
        description: description.trim() || undefined,
        cover_image_url: coverImageUrl || undefined,
        parent_collection_id: parentCollectionId || undefined,
      };

      await onSubmit(collectionData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save collection');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Filter out current collection and its descendants to prevent circular nesting
  const selectableCollections = availableCollections.filter(c => {
    if (currentCollectionId && c.id === currentCollectionId) {
      return false;
    }
    // Also filter out collections that are already at max nesting level
    return c.nesting_level < 2;
  });

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto space-y-6">
      {error && (
        <div 
          className="comic-border bg-destructive/10 border-destructive text-destructive px-6 py-4 font-bold animate-shake" 
          role="alert"
        >
          ⚠️ {error}
        </div>
      )}

      {/* Name */}
      <div>
        <label htmlFor="name" className="block comic-label text-foreground mb-3">
          Collection Name <span className="text-destructive">*</span>
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full comic-input px-4 py-3 text-lg font-medium"
          placeholder="Enter collection name"
          aria-required="true"
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block comic-label text-foreground mb-3">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full comic-input px-4 py-3 font-medium resize-none"
          placeholder="Enter collection description"
          rows={3}
        />
      </div>

      {/* Cover Image */}
      <div>
        <label className="block comic-label text-foreground mb-3">
          Cover Image
        </label>
        <ImageUpload 
          onImageUploaded={handleImageUploaded} 
          initialImageUrl={coverImageUrl}
        />
      </div>

      {/* Parent Collection */}
      {selectableCollections.length > 0 && (
        <div>
          <label htmlFor="parentCollection" className="block comic-label text-foreground mb-3">
            Parent Collection (Optional)
          </label>
          <select
            id="parentCollection"
            value={parentCollectionId || ''}
            onChange={(e) => setParentCollectionId(e.target.value ? Number(e.target.value) : undefined)}
            className="w-full comic-input px-4 py-3 font-medium"
            aria-label="Select parent collection"
          >
            <option value="">None (Top Level)</option>
            {selectableCollections.map(collection => (
              <option key={collection.id} value={collection.id}>
                {'  '.repeat(collection.nesting_level)}{collection.name}
              </option>
            ))}
          </select>
          <p className="mt-2 text-sm text-muted-foreground font-medium">
            Maximum nesting level: 3
          </p>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex gap-4 pt-6">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 comic-button bg-primary text-primary-foreground py-4 px-8 text-xl disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'SAVING...' : submitLabel.toUpperCase()}
        </button>
      </div>
    </form>
  );
}
