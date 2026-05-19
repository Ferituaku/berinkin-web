'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function BottomNavBar() {
  const pathname = usePathname();

  const navLinks = [
    { name: 'Beranda', path: '/', icon: 'home' },
    { name: 'Peringkas', path: '/peringkas', icon: 'auto_stories' },
    { name: 'Hasil', path: '/hasil', icon: 'analytics' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center h-16 bg-background/90 md:hidden border-t-[0.5px] border-outline-variant backdrop-blur-lg pb-safe">
      {navLinks.map((link) => {
        const isActive = pathname === link.path;
        return (
          <Link 
            key={link.path}
            href={link.path}
            className={`flex flex-col items-center justify-center transition-colors scale-95 active:scale-90 transition-transform ${isActive ? 'text-primary font-bold' : 'text-outline hover:text-primary'}`}
          >
            <span className="material-symbols-outlined mb-1" style={isActive ? { fontVariationSettings: "'FILL' 1" } : {}}>{link.icon}</span>
            <span className="font-[family-name:var(--font-newsreader)] text-[10px] uppercase tracking-widest">{link.name}</span>
          </Link>
        );
      })}
    </nav>
  );
}
