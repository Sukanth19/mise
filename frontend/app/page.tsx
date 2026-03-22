'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AuthForm from '@/components/AuthForm';
import { apiClient, setToken } from '@/lib/api';
import { AuthToken } from '@/types';

export default function Home() {
  const router = useRouter();

  const handleLogin = async (username: string, password: string) => {
    const data = await apiClient<AuthToken>('/api/auth/login', {
      method: 'POST',
      requiresAuth: false,
      body: JSON.stringify({ username, password }),
    });

    setToken(data.access_token);
    router.push('/dashboard');
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md px-6">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Recipe Saver</h1>
          <p className="text-gray-600">Log in to your account</p>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-md">
          <AuthForm mode="login" onSubmit={handleLogin} />

          <div className="mt-4 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/register" className="text-blue-600 hover:underline">
              Register here
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
