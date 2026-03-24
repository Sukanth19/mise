'use client';

import Link from 'next/link';

interface Comment {
  id: number;
  recipe_id: number;
  user_id: number;
  comment_text: string;
  created_at: string;
  author: {
    id: number;
    username: string;
  };
}

interface CommentListProps {
  comments: Comment[];
}

export default function CommentList({ comments }: CommentListProps) {
  if (comments.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        No comments yet. Be the first to comment!
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {comments.map((comment) => {
        const formattedDate = new Date(comment.created_at).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        });

        return (
          <div
            key={comment.id}
            className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4"
          >
            <div className="flex items-start gap-3">
              {/* Avatar */}
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                {comment.author.username.charAt(0).toUpperCase()}
              </div>

              <div className="flex-1 min-w-0">
                {/* Author and Date */}
                <div className="flex items-center gap-2 mb-1">
                  <Link
                    href={`/users/${comment.author.id}`}
                    className="font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400"
                  >
                    {comment.author.username}
                  </Link>
                  <span className="text-xs text-gray-500 dark:text-gray-500">
                    {formattedDate}
                  </span>
                </div>

                {/* Comment Text */}
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">
                  {comment.comment_text}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
