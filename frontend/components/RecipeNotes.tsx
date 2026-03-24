'use client';

import { Note } from '@/types';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, Plus } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface RecipeNotesProps {
  recipeId: number;
  initialNotes?: Note[];
}

export default function RecipeNotes({ recipeId, initialNotes = [] }: RecipeNotesProps) {
  const [notes, setNotes] = useState<Note[]>(initialNotes);
  const [noteText, setNoteText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!noteText.trim()) {
      setError('Note text cannot be empty');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const newNote = await apiClient<Note>(`/api/recipes/${recipeId}/notes`, {
        method: 'POST',
        body: JSON.stringify({ note_text: noteText.trim() }),
      });
      
      setNotes([...notes, newNote]);
      setNoteText('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add note');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm('Are you sure you want to delete this note?')) {
      return;
    }

    try {
      await apiClient(`/api/recipes/${recipeId}/notes/${noteId}`, {
        method: 'DELETE',
      });
      
      setNotes(notes.filter(note => note.id !== noteId));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete note');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.9 }}
      className="mb-8"
    >
      <h2 className="text-2xl comic-heading text-foreground mb-4">Personal Notes</h2>
      
      {/* Add Note Form */}
      <form onSubmit={handleAddNote} className="mb-6">
        <div className="flex flex-col gap-3">
          <textarea
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Add a personal note about this recipe..."
            className="w-full p-4 comic-border bg-background text-foreground font-medium resize-none focus:outline-none focus:ring-2 focus:ring-ring min-h-[100px]"
            disabled={isSubmitting}
          />
          {error && (
            <p className="text-destructive text-sm font-bold">{error}</p>
          )}
          <button
            type="submit"
            disabled={isSubmitting || !noteText.trim()}
            className="self-start comic-button px-6 py-3 bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Plus size={20} strokeWidth={2.5} />
            {isSubmitting ? 'ADDING...' : 'ADD NOTE'}
          </button>
        </div>
      </form>

      {/* Notes List */}
      <div className="space-y-4">
        <AnimatePresence mode="popLayout">
          {notes.length === 0 ? (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-muted-foreground italic font-medium"
            >
              No notes yet. Add your first note above!
            </motion.p>
          ) : (
            notes.map((note, index) => (
              <motion.div
                key={note.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ delay: index * 0.05 }}
                className="comic-border bg-card p-4 relative group"
              >
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1">
                    <p className="text-foreground font-medium whitespace-pre-wrap mb-2">
                      {note.note_text}
                    </p>
                    <p className="text-sm text-muted-foreground font-bold">
                      {formatDate(note.created_at)}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteNote(note.id)}
                    className="flex-shrink-0 p-2 text-destructive hover:bg-destructive/10 comic-border transition-colors opacity-0 group-hover:opacity-100"
                    aria-label="Delete note"
                  >
                    <Trash2 size={18} strokeWidth={2.5} />
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
