'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
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
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8"
        >
          <motion.div 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ 
              duration: 0.6,
              ease: [0.34, 1.56, 0.64, 1]
            }}
            className="flex justify-center mb-6"
          >
            <svg className="w-24 h-24" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <rect width="100" height="100" rx="0" fill="#FF8C00" stroke="#0D0D0D" strokeWidth="5"/>
              <path d="M25 50 L45 30 L48 33 L28 53 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="3"/>
              <path d="M45 30 L48 27 L51 30 L48 33 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="3"/>
              <rect x="20" y="55" width="60" height="6" rx="0" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
              <motion.circle 
                cx="35" 
                cy="70" 
                r="4" 
                fill="#00D9A3" 
                stroke="#0D0D0D" 
                strokeWidth="3"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.8, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              <motion.circle 
                cx="42" 
                cy="68" 
                r="3" 
                fill="#00D9A3" 
                stroke="#0D0D0D" 
                strokeWidth="3"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.8, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.3
                }}
              />
              <motion.circle 
                cx="55" 
                cy="69" 
                r="4" 
                fill="#00D9A3" 
                stroke="#0D0D0D" 
                strokeWidth="3"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.8, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.6
                }}
              />
            </svg>
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="text-5xl comic-heading mb-4 text-foreground"
          >
            MISE
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="text-muted-foreground font-bold uppercase tracking-wide"
          >
            Create your account
          </motion.p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="comic-panel bg-card p-8 rounded-none"
        >
          <AuthForm mode="register" onSubmit={handleRegister} />

          <div className="mt-6 text-center text-sm font-bold">
            Already have an account?{' '}
            <Link href="/" className="text-accent underline hover:text-accent-hover transition-colors">
              LOG IN HERE
            </Link>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
