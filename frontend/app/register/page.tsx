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
    <main className="min-h-screen flex items-center justify-center bg-background halftone-bg">
      <div className="w-full max-w-md px-6">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6">
            <svg className="w-24 h-24" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <rect width="100" height="100" rx="0" fill="#FF8C00" stroke="#0D0D0D" strokeWidth="5"/>
              <path d="M25 50 L45 30 L48 33 L28 53 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="3"/>
              <path d="M45 30 L48 27 L51 30 L48 33 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="3"/>
              <rect x="20" y="55" width="60" height="6" rx="0" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
              <circle cx="35" cy="70" r="4" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="3"/>
              <circle cx="42" cy="68" r="3" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="3"/>
              <circle cx="55" cy="69" r="4" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="3"/>
            </svg>
          </div>
          <h1 className="text-5xl comic-heading mb-4 text-foreground">MISE</h1>
          <p className="text-muted-foreground font-bold uppercase tracking-wide">Create your account</p>
        </div>

        <div className="comic-panel bg-card p-8 rounded-none">
          <AuthForm mode="register" onSubmit={handleRegister} />

          <div className="mt-6 text-center text-sm font-bold">
            Already have an account?{' '}
            <Link href="/" className="text-accent underline hover:text-accent-hover">
              LOG IN HERE
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
