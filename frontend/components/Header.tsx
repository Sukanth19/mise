'use client';

import { useRouter, usePathname } from 'next/navigation';
import { removeToken } from '@/lib/api';
import { motion } from 'framer-motion';
import ThemeToggle from '@/components/ThemeToggle';

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
    <header className="sticky top-0 z-50 border-b-[5px] border-border bg-background comic-border-thick">
      <div className="container mx-auto px-4 h-20 flex items-center justify-between">
        <button 
          type="button"
          onClick={() => {
            if (pathname === '/dashboard') {
              window.location.reload();
            } else {
              router.push('/dashboard');
            }
          }}
          className="flex items-center gap-3 comic-button bg-primary text-primary-foreground px-4 py-2 rounded-none group"
        >
          <motion.svg 
            className="w-10 h-10" 
            viewBox="0 0 100 100" 
            xmlns="http://www.w3.org/2000/svg"
            whileHover={{ rotate: [0, -5, 5, -5, 0] }}
            transition={{ duration: 0.5 }}
          >
            <rect width="100" height="100" rx="0" fill="#FF8C00" stroke="#0D0D0D" strokeWidth="4"/>
            <path d="M25 50 L45 30 L48 33 L28 53 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
            <path d="M45 30 L48 27 L51 30 L48 33 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
            <rect x="20" y="55" width="60" height="5" rx="0" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
            <circle cx="35" cy="70" r="4" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="2"/>
            <circle cx="42" cy="68" r="3" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="2"/>
            <circle cx="55" cy="69" r="4" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="2"/>
          </motion.svg>
          <h1 className="text-2xl comic-heading">MISE</h1>
        </button>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <button
            type="button"
            onClick={handleSignOut}
            className="comic-button px-6 py-3 rounded-none bg-accent hover:bg-accent-hover text-accent-foreground"
          >
            SIGN OUT
          </button>
        </div>
      </div>
    </header>
  );
}
