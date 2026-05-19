'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

export default function Header() {
  const pathname = usePathname();

  const navLinks = [
    { name: 'Beranda', path: '/' },
    { name: 'Peringkas', path: '/peringkas' },
    { name: 'Hasil', path: '/hasil' },
  ];

  return (
    <header className="fixed top-0 w-full z-40 bg-background/80 backdrop-blur-xl border-b-[0.5px] border-outline-variant transition-all ease-in-out duration-300 hidden md:block">
      <div className="flex justify-between items-center px-8 h-20 w-full max-w-[1200px] mx-auto">
        {/* Brand */}
        <Link href="/" className="text-2xl font-bold text-primary font-[family-name:var(--font-newsreader)] tracking-tight">
          Berin'kin
        </Link>
        
        {/* Navigation moved to right, profile logo removed */}
        <nav className="flex gap-8 items-center relative">
          {navLinks.map((link) => {
            const isActive = pathname === link.path;
            return (
              <Link 
                key={link.path}
                href={link.path}
                className={`relative font-[family-name:var(--font-newsreader)] tracking-tight py-1 transition-colors hover:opacity-80 ${isActive ? 'text-primary' : 'text-outline hover:text-primary'}`}
              >
                {link.name}
                {isActive && (
                  <motion.div
                    layoutId="activeNav"
                    className="absolute bottom-0 left-0 right-0 h-[2px] bg-primary"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
