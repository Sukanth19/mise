'use client';

import { useTransition } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { removeToken } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import ThemeToggle from '@/components/ThemeToggle';
import { 
  Home, 
  FolderOpen, 
  Calendar, 
  ShoppingCart, 
  Compass, 
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';

export default function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Don't show header on login/register pages
  if (pathname === '/' || pathname === '/register') {
    return null;
  }

  const handleSignOut = async () => {
    removeToken();
    // Force a hard navigation to clear all state
    window.location.href = '/';
  };

  const navLinks = [
    { href: '/dashboard', label: 'MY RECIPES', icon: Home },
    { href: '/collections', label: 'COLLECTIONS', icon: FolderOpen },
    { href: '/meal-planner', label: 'MEAL PLANNER', icon: Calendar },
    { href: '/shopping-lists', label: 'SHOPPING', icon: ShoppingCart },
    { href: '/discover', label: 'DISCOVER', icon: Compass },
  ];

  return (
    <header className="sticky top-0 z-50 border-b-[5px] border-border bg-background comic-border-thick shadow-lg peppermint-glow">
      <div className="container mx-auto px-4 h-20 flex items-center justify-between gap-4">
        {/* Logo - Left Side */}
        <Link 
          href="/dashboard"
          className="flex items-center gap-3 comic-button bg-primary text-primary-foreground px-4 py-2 rounded-none group hover:scale-105 transition-transform"
        >
          <motion.svg 
            className="w-10 h-10" 
            viewBox="0 0 100 100" 
            xmlns="http://www.w3.org/2000/svg"
            whileHover={{ rotate: [0, -5, 5, -5, 0] }}
            transition={{ duration: 0.5 }}
          >
            <defs>
              <filter id="peppermint-glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <rect width="100" height="100" rx="0" fill="#FF8C00" stroke="#0D0D0D" strokeWidth="4"/>
            <rect x="2" y="2" width="96" height="96" rx="0" fill="none" stroke="#2D6A4F" strokeWidth="2" opacity="0.6" filter="url(#peppermint-glow)"/>
            <path d="M25 50 L45 30 L48 33 L28 53 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
            <path d="M45 30 L48 27 L51 30 L48 33 Z" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
            <rect x="20" y="55" width="60" height="5" rx="0" fill="#0D0D0D" stroke="#0D0D0D" strokeWidth="2"/>
            <circle cx="35" cy="70" r="4" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="2" filter="url(#peppermint-glow)"/>
            <circle cx="42" cy="68" r="3" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="2" filter="url(#peppermint-glow)"/>
            <circle cx="55" cy="69" r="4" fill="#2D6A4F" stroke="#0D0D0D" strokeWidth="2" filter="url(#peppermint-glow)"/>
          </motion.svg>
          <h1 className="text-2xl comic-heading hidden sm:block">MISE</h1>
        </Link>

        {/* Desktop Navigation - Center */}
        <nav className="hidden lg:flex items-center gap-2 flex-1 justify-center">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`comic-button px-4 py-2 text-sm flex items-center gap-2 transition-all ${
                  isActive
                    ? 'bg-primary text-primary-foreground peppermint-glow scale-105'
                    : 'bg-primary text-primary-foreground hover:scale-105'
                }`}
              >
                <Icon size={16} strokeWidth={2.5} />
                <span className="font-black">{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Mobile Menu Button */}
        <button
          type="button"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="lg:hidden comic-button p-3 bg-muted text-muted-foreground"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X size={24} strokeWidth={2.5} /> : <Menu size={24} strokeWidth={2.5} />}
        </button>

        {/* Theme Toggle and Sign Out - Right Side */}
        <div className="hidden lg:flex items-center gap-4">
          <ThemeToggle />
          <button
            type="button"
            onClick={handleSignOut}
            className="comic-button px-6 py-3 rounded-none bg-primary hover:bg-primary/90 text-primary-foreground flex items-center gap-2 hover:scale-105 transition-transform"
          >
            <LogOut size={18} strokeWidth={2.5} />
            <span className="font-black">SIGN OUT</span>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="lg:hidden border-t-4 border-border bg-card overflow-hidden"
          >
            <nav className="container mx-auto px-4 py-4 space-y-2">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = pathname.startsWith(link.href);
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`comic-button px-4 py-3 text-sm flex items-center gap-3 w-full ${
                      isActive
                        ? 'bg-primary text-primary-foreground peppermint-glow'
                        : 'bg-primary text-primary-foreground hover:brightness-110'
                    }`}
                  >
                    <Icon size={18} strokeWidth={2.5} />
                    <span className="font-black">{link.label}</span>
                  </Link>
                );
              })}
              <div className="flex items-center gap-2 pt-4 border-t-4 border-border">
                <ThemeToggle />
                <button
                  type="button"
                  onClick={handleSignOut}
                  className="comic-button px-6 py-3 rounded-none bg-primary hover:bg-primary/90 text-primary-foreground flex items-center gap-2 flex-1"
                >
                  <LogOut size={18} strokeWidth={2.5} />
                  <span className="font-black">SIGN OUT</span>
                </button>
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

