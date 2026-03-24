'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getToken } from '@/lib/api';
import UserProfile from '@/components/UserProfile';

export default function UserProfilePage() {
  const params = useParams();
  const userId = parseInt(params.id as string);
  const [currentUserId, setCurrentUserId] = useState<number | undefined>(undefined);

  useEffect(() => {
    // Try to get current user ID from token
    const token = getToken();
    if (token) {
      try {
        // Decode JWT to get user ID (simple base64 decode of payload)
        const payload = JSON.parse(atob(token.split('.')[1]));
        setCurrentUserId(payload.sub || payload.user_id);
      } catch (error) {
        console.error('Failed to decode token:', error);
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <UserProfile userId={userId} currentUserId={currentUserId} />
      </div>
    </div>
  );
}
