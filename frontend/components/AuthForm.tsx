'use client';

import { useState, FormEvent } from 'react';
import LoginAnimation from './LoginAnimation';

interface AuthFormProps {
  mode: 'login' | 'register';
  onSubmit: (username: string, password: string) => Promise<void>;
}

export default function AuthForm({ mode, onSubmit }: AuthFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // Client-side validation
    if (!username.trim()) {
      setError('Username is required');
      return;
    }

    if (!password) {
      setError('Password is required');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);
    try {
      await onSubmit(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="w-full max-w-md flex items-center justify-center py-12">
        <LoginAnimation />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md space-y-6">
      <div>
        <label htmlFor="username" className="block text-sm font-black text-foreground mb-2 uppercase tracking-wide">
          Username
        </label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full px-4 py-3 comic-input rounded-none font-bold"
          disabled={isLoading}
          required
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-black text-foreground mb-2 uppercase tracking-wide">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-3 comic-input rounded-none font-bold"
          disabled={isLoading}
          required
        />
      </div>

      {error && (
        <div className="comic-panel bg-destructive text-destructive-foreground p-4 rounded-none font-bold animate-shake" role="alert">
          ⚠️ {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full comic-button bg-primary text-primary-foreground py-4 px-6 rounded-none disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'LOADING...' : mode === 'login' ? 'LOG IN' : 'REGISTER'}
      </button>
    </form>
  );
}
