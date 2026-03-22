'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AuthForm from '@/components/AuthForm';
import { apiClient, setToken } from '@/lib/api';
import { AuthToken } from '@/types';

export default function RegisterPage() {
  const router = useRouter();

  const handleRegister = async (username: string, password: string) => {
    // First register the user
    await apiClient('/api/auth/register', {
      method: 'POST',
      requiresAuth: false,
      body: JSON.stringify({ username, password }),
    });

    // Then log them in
    const data = await apiClient<AuthToken>('/api/auth/login', {
      method: 'POST',
      requiresAuth: false,
      body: JSON.stringify({ username, password }),
    });

    setToken(data.access_token);
    router.push('/dashboard');
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md px-6">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <svg className="w-20 h-20" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="grad-register" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#8B5CF6', stopOpacity: 1 }} />
                  <stop offset="100%" style={{ stopColor: '#EC4899', stopOpacity: 1 }} />
                </linearGradient>
              </defs>
              <rect width="100" height="100" rx="22" fill="url(#grad-register)"/>
              <path d="M25 50 L45 30 L48 33 L28 53 Z" fill="white" opacity="0.95"/>
              <path d="M45 30 L48 27 L51 30 L48 33 Z" fill="white" opacity="0.8"/>
              <rect x="20" y="55" width="60" height="4" rx="1" fill="white" opacity="0.9"/>
              <circle cx="35" cy="68" r="3" fill="#2D6A4F" opacity="0.9"/>
              <circle cx="42" cy="66" r="2.5" fill="#2D6A4F" opacity="0.9"/>
              <circle cx="38" cy="72" r="2" fill="#2D6A4F" opacity="0.9"/>
              <circle cx="55" cy="67" r="3" fill="#2D6A4F" opacity="0.9"/>
              <circle cx="60" cy="70" r="2.5" fill="#2D6A4F" opacity="0.9"/>
            </svg>
          </div>
          <h1 className="text-4xl font-bold mb-2 text-foreground tracking-tight">Mise</h1>
          <p className="text-muted-foreground">Create your account</p>
        </div>

        <div className="bg-card p-8 rounded-lg shadow-lg border border-border">
          <AuthForm mode="register" onSubmit={handleRegister} />

          <div className="mt-4 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link href="/" className="text-primary hover:underline">
              Log in here
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
