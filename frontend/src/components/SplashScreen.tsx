'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';
import Image from 'next/image';

export default function SplashScreen({ children }: { children: React.ReactNode }) {
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    // Hide splash screen after 2.5 seconds
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <AnimatePresence>
        {showSplash && (
          <motion.div
            key="splash"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            className="fixed inset-0 z-[9999] bg-background flex flex-col items-center justify-center"
          >
            <motion.div
              animate={{ 
                scale: [1, 1.05, 1],
                opacity: [0.7, 1, 0.7]
              }}
              transition={{
                duration: 2,
                ease: "easeInOut",
                repeat: Infinity,
                repeatType: "loop"
              }}
              className="flex flex-col items-center"
            >
              <div className="relative w-32 h-32 mb-6">
                <Image 
                  src="/banyan.png" 
                  alt="Berinkin Logo" 
                  fill 
                  className="object-contain opacity-90 mix-blend-multiply dark:mix-blend-normal"
                  priority
                />
              </div>
              <h1 className="font-[family-name:var(--font-newsreader)] text-[32px] text-primary tracking-widest font-medium">
                Berin'kin
              </h1>
              <p className="font-[family-name:var(--font-inter)] text-[12px] text-outline tracking-[0.2em] uppercase mt-2">
                Berita Ringkas Terkini
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      {children}
    </>
  );
}
