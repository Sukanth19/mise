'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, getToken } from '@/lib/api';
import { Collection, CollectionCreate, CollectionUpdate } from '@/types';
import CollectionGrid from '@/components/CollectionGrid';
import CollectionForm from '@/components/CollectionForm';
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal';
import LoadingSpinner from '@/components/LoadingSpinner';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus } from 'lucide-react';

export default function CollectionsPage() {
  const router = useRouter();
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedCollection, setSelectedCollection] = useState<Collection | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchCollections();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchCollections = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch data
      const data = await apiClient<{ collections: Collection[] }>('/api/collections');
      
      setCollections(data.collections || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch collections');
      setCollections([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCollection = async (data: CollectionCreate | CollectionUpdate) => {
    try {
      await apiClient('/api/collections', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      setShowCreateModal(false);
      await fetchCollections();
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create collection');
    }
  };

  const handleEditCollection = async (data: CollectionCreate | CollectionUpdate) => {
    if (!selectedCollection) return;

    try {
      await apiClient(`/api/collections/${selectedCollection.id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      setShowEditModal(false);
      setSelectedCollection(null);
      await fetchCollections();
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update collection');
    }
  };

  const handleDeleteCollection = async () => {
    if (!selectedCollection) return;

    try {
      setIsDeleting(true);
      await apiClient(`/api/collections/${selectedCollection.id}`, {
        method: 'DELETE',
      });
      setShowDeleteModal(false);
      setSelectedCollection(null);
      await fetchCollections();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete collection');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleEdit = (collection: Collection) => {
    setSelectedCollection(collection);
    setShowEditModal(true);
  };

  const handleDelete = (collection: Collection) => {
    setSelectedCollection(collection);
    setShowDeleteModal(true);
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-background halftone-bg p-8 flex items-center justify-center">
        <LoadingSpinner variant="collection" size="lg" text="Loading collections..." />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background halftone-bg p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <h1 className="text-4xl comic-heading text-foreground mb-4 md:mb-0">MY COLLECTIONS</h1>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="comic-button px-8 py-4 bg-primary text-primary-foreground rounded-none flex items-center gap-2"
          >
            <Plus size={20} strokeWidth={3} />
            CREATE COLLECTION
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 comic-panel bg-destructive text-destructive-foreground p-4 rounded-none font-bold">
            {error}
          </div>
        )}

        {/* Empty State */}
        {!loading && collections && collections.length === 0 && (
          <div className="text-center py-12">
            <div className="mb-6">
              <div className="text-8xl mb-4">📁</div>
            </div>
            <h2 className="text-2xl font-black text-foreground mb-3 uppercase">No collections yet</h2>
            <p className="text-muted-foreground mb-8 font-bold uppercase">
              Organize your recipes into collections!
            </p>
            <button
              type="button"
              onClick={() => setShowCreateModal(true)}
              className="comic-button px-8 py-4 bg-primary text-primary-foreground rounded-none"
            >
              CREATE YOUR FIRST COLLECTION
            </button>
          </div>
        )}

        {/* Collection Grid */}
        {!loading && collections && collections.length > 0 && (
          <CollectionGrid 
            collections={collections} 
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}

        {/* Create Collection Modal */}
        <AnimatePresence>
          {showCreateModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
              onClick={(e) => {
                if (e.target === e.currentTarget) {
                  setShowCreateModal(false);
                }
              }}
              role="dialog"
              aria-modal="true"
              aria-labelledby="create-modal-title"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 30 }}
                transition={{ 
                  duration: 0.3,
                  ease: [0.4, 0, 0.2, 1]
                }}
                className="comic-panel bg-card w-full max-w-3xl max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between p-6 border-b-4 border-border sticky top-0 bg-card z-10">
                  <h2 id="create-modal-title" className="text-2xl font-black uppercase tracking-wide">
                    Create Collection
                  </h2>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="comic-button p-2 bg-secondary text-secondary-foreground"
                    aria-label="Close modal"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="p-6">
                  <CollectionForm
                    onSubmit={handleCreateCollection}
                    submitLabel="Create Collection"
                    availableCollections={collections}
                  />
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Edit Collection Modal */}
        <AnimatePresence>
          {showEditModal && selectedCollection && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
              onClick={(e) => {
                if (e.target === e.currentTarget) {
                  setShowEditModal(false);
                  setSelectedCollection(null);
                }
              }}
              role="dialog"
              aria-modal="true"
              aria-labelledby="edit-modal-title"
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 30 }}
                transition={{ 
                  duration: 0.3,
                  ease: [0.4, 0, 0.2, 1]
                }}
                className="comic-panel bg-card w-full max-w-3xl max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between p-6 border-b-4 border-border sticky top-0 bg-card z-10">
                  <h2 id="edit-modal-title" className="text-2xl font-black uppercase tracking-wide">
                    Edit Collection
                  </h2>
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedCollection(null);
                    }}
                    className="comic-button p-2 bg-secondary text-secondary-foreground"
                    aria-label="Close modal"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="p-6">
                  <CollectionForm
                    initialData={selectedCollection}
                    onSubmit={handleEditCollection}
                    submitLabel="Update Collection"
                    availableCollections={collections}
                    currentCollectionId={selectedCollection.id}
                  />
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Delete Confirmation Modal */}
        <DeleteConfirmationModal
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setSelectedCollection(null);
          }}
          onConfirm={handleDeleteCollection}
          title={selectedCollection?.name || ''}
          isDeleting={isDeleting}
        />
      </div>
    </main>
  );
}
