'use client';

import { useRouter, usePathname } from 'next/navigation';
import { removeToken } from '@/lib/api';

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();

  // Don't show header on login/register pages
  if (pathname === '/' || pathname === '/register') {
    return null;
  }

  const handleSignOut = () => {
    removeToken();
    router.push('/');
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <button 
          onClick={() => {
            if (pathname === '/dashboard') {
              window.location.reload();
            } else {
              router.push('/dashboard');
            }
          }}
          className="flex items-center gap-3 hover:opacity-80 transition-opacity"
        >
          <svg className="w-9 h-9" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="grad-header" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: '#8B5CF6', stopOpacity: 1 }} />
                <stop offset="100%" style={{ stopColor: '#EC4899', stopOpacity: 1 }} />
              </linearGradient>
            </defs>
            <rect width="100" height="100" rx="22" fill="url(#grad-header)"/>
            <path d="M25 50 L45 30 L48 33 L28 53 Z" fill="white" opacity="0.95"/>
            <path d="M45 30 L48 27 L51 30 L48 33 Z" fill="white" opacity="0.8"/>
            <rect x="20" y="55" width="60" height="4" rx="1" fill="white" opacity="0.9"/>
            <circle cx="35" cy="68" r="3" fill="#2D6A4F" opacity="0.9"/>
            <circle cx="42" cy="66" r="2.5" fill="#2D6A4F" opacity="0.9"/>
            <circle cx="38" cy="72" r="2" fill="#2D6A4F" opacity="0.9"/>
            <circle cx="55" cy="67" r="3" fill="#2D6A4F" opacity="0.9"/>
            <circle cx="60" cy="70" r="2.5" fill="#2D6A4F" opacity="0.9"/>
          </svg>
          <h1 className="text-xl font-semibold text-foreground tracking-tight">Mise</h1>
        </button>

        <div className="flex items-center gap-3">
          {/* Sign Out Button */}
          <button
            onClick={handleSignOut}
            className="px-4 py-2 rounded-lg bg-accent hover:bg-accent-hover text-foreground font-medium transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}
