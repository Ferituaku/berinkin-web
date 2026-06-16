'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Peringkas() {
  const router = useRouter();
  const [category, setCategory] = useState('tekno');
  const [date, setDate] = useState(() => {
    if (typeof window !== 'undefined') {
      const tzOffset = (new Date()).getTimezoneOffset() * 60000;
      return (new Date(Date.now() - tzOffset)).toISOString().split('T')[0];
    }
    return '';
  });
  const [maxArticles, setMaxArticles] = useState(15);
  const [compression, setCompression] = useState(30);
  const [lambda, setLambda] = useState(0.7);
  const [loading, setLoading] = useState(false);
  
  const [progress, setProgress] = useState(0);
  const [loadingText, setLoadingText] = useState('Menginisialisasi...');

  useEffect(() => {
    if (loading) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    }
  }, [loading]);

  const handleSummarize = async () => {
    setLoading(true);
    setProgress(0);
    setLoadingText("Memulai koneksi ke server...");
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category, date, max_articles: maxArticles, compression, lambda_param: lambda })
      });
      
      if (!response.body) {
          throw new Error('ReadableStream not supported');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        let eolIndex;
        while ((eolIndex = buffer.indexOf('\n\n')) >= 0) {
            const eventString = buffer.slice(0, eolIndex).trim();
            buffer = buffer.slice(eolIndex + 2);
            
            if (eventString.startsWith('data: ')) {
                try {
                    const data = JSON.parse(eventString.slice(6));
                    if (data.progress) setProgress(data.progress);
                    if (data.message) setLoadingText(data.message);
                    
                    if (data.status === 'success' && data.clusters) {
                        localStorage.setItem('berinkin_clusters', JSON.stringify(data.clusters));
                        setTimeout(() => {
                           router.push('/hasil');
                        }, 500);
                        return; // Done
                    } else if (data.status === 'error') {
                        alert("Terjadi kesalahan: " + data.message);
                        setLoading(false);
                        return;
                    }
                } catch(e) {
                   console.error("SSE Parse Error:", e);
                }
            }
        }
      }
    } catch (error) {
      console.error("Error during summarization:", error);
      alert("Gagal terhubung ke server backend. Pastikan uvicorn berjalan.");
      setLoading(false);
    }
  };

  return (
    <>
      {/* Loading Overlay */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-md flex flex-col items-center justify-center p-8"
          >
            {/* Visual Metaphor: Convergence Grid/Lines */}
            <div className="absolute inset-0 z-0 pointer-events-none opacity-20">
              <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-gradient-to-b from-transparent via-primary to-transparent transform -translate-x-1/2"></div>
              <div className="absolute top-1/2 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary/30 to-transparent transform -translate-y-1/2"></div>
              <div className="absolute top-[20%] left-0 w-1/2 h-[1px] bg-gradient-to-r from-transparent to-primary/20 rotate-[15deg] transform origin-right"></div>
              <div className="absolute top-[80%] left-0 w-1/2 h-[1px] bg-gradient-to-r from-transparent to-primary/20 -rotate-[15deg] transform origin-right"></div>
              <div className="absolute top-[30%] right-0 w-1/2 h-[1px] bg-gradient-to-l from-transparent to-primary/20 -rotate-[10deg] transform origin-left"></div>
              <div className="absolute top-[70%] right-0 w-1/2 h-[1px] bg-gradient-to-l from-transparent to-primary/20 rotate-[10deg] transform origin-left"></div>
            </div>

            {/* Central Node Container (Glassmorphic) */}
            <motion.div 
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              className="relative z-10 w-full max-w-[600px] bg-surface/90 backdrop-blur-[16px] border-[0.5px] border-outline-variant p-16 flex flex-col items-center justify-center shadow-2xl rounded-lg overflow-hidden"
            >
              {/* Animated Progress Background Overlay (Optional subtlety) */}
              <div 
                className="absolute bottom-0 left-0 h-1 bg-primary/20 transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              ></div>

              {/* Content */}
              <div className="text-center space-y-6 w-full relative z-10">
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                  className="text-primary mb-6 inline-block"
                >
                  <span className="material-symbols-outlined text-[48px] font-light">all_inclusive</span>
                </motion.div>
                
                <h1 className="font-[family-name:var(--font-newsreader)] text-[40px] leading-[1.1] text-on-surface m-0 px-4 font-semibold">
                  Menenun Ringkasan...
                </h1>
                
                <div className="flex flex-col items-center justify-center mt-6">
                  <div className="font-[family-name:var(--font-inter)] text-[40px] font-medium text-primary tracking-tighter tabular-nums">
                    {progress.toFixed(0)}<span className="text-[20px] opacity-60 ml-1">%</span>
                  </div>
                  <p className="font-[family-name:var(--font-inter)] text-[12px] text-primary/80 tracking-[0.1em] uppercase mt-2 font-medium min-h-[18px] transition-all">
                      {loadingText}
                  </p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="px-4 md:px-10 max-w-[1200px] mx-auto w-full relative z-10">
        {/* Header Section */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="mb-16 text-center max-w-2xl mx-auto">
          <h1 className="font-[family-name:var(--font-newsreader)] text-[48px] leading-[1.1] text-primary mb-4 tracking-tight font-semibold">Ringkasan Pikiran</h1>
          <p className="font-[family-name:var(--font-inter)] text-[18px] leading-[1.6] text-on-surface-variant font-light">Konfigurasikan parameter ekstraksi untuk mensintesis berita hari ini secara mendalam.</p>
        </motion.div>

        {/* Configuration Form Area */}
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, delay: 0.2 }} className="max-w-xl mx-auto bg-white/80 backdrop-blur-[12px] border-[0.5px] border-outline-variant p-8 relative rounded-[0.125rem]">
          {/* Network Nodes */}
          <div className="absolute -top-[3px] -left-[3px] w-1.5 h-1.5 bg-primary-container"></div>
          <div className="absolute -top-[3px] -right-[3px] w-1.5 h-1.5 bg-primary-container"></div>
          <div className="absolute -bottom-[3px] -left-[3px] w-1.5 h-1.5 bg-primary-container"></div>
          <div className="absolute -bottom-[3px] -right-[3px] w-1.5 h-1.5 bg-primary-container"></div>

          <form className="space-y-10" onSubmit={(e) => e.preventDefault()}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Category Field */}
                <div className="space-y-2">
                  <label className="block font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold">Kategori Berita</label>
                  <div className="relative">
                    <select 
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full bg-transparent border-0 border-b border-surface-tint focus:border-primary-container focus:outline-none px-0 py-3 font-[family-name:var(--font-inter)] text-[16px] text-on-surface appearance-none cursor-pointer"
                    >
                      <option value="tekno">Teknologi &amp; Inovasi</option>
                      <option value="crypto">Kripto &amp; Blockchain</option>
                      <option value="bola">Sepak Bola &amp; Olahraga</option>
                      <option value="otomotif">Otomotif &amp; Kendaraan</option>
                      <option value="health">Kesehatan &amp; Gaya Hidup</option>
                      <option value="saham">Pasar Saham</option>
                      <option value="bisnis">Bisnis &amp; Ekonomi</option>
                    </select>
                    <span className="material-symbols-outlined absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none text-surface-tint">expand_more</span>
                  </div>
                </div>

                {/* Date Range Field */}
                <div className="space-y-2">
                  <label className="block font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold">Tanggal Berita</label>
                  <div className="relative w-full">
                    <input 
                      type="date" 
                      value={date}
                      onChange={(e) => setDate(e.target.value)}
                      className="w-full bg-transparent border-0 border-b border-surface-tint focus:border-primary-container focus:outline-none px-0 py-3 font-[family-name:var(--font-inter)] text-[16px] text-on-surface cursor-pointer" 
                    />
                  </div>
                </div>
            </div>

            {/* Jumlah Berita Field */}
            <div className="space-y-2">
              <div className="flex justify-between items-end">
                <label className="block font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold">Target Jumlah Berita</label>
                <span className="font-[family-name:var(--font-inter)] text-[12px] text-primary-container font-semibold">{maxArticles} Artikel</span>
              </div>
              <input 
                  className="editorial-slider w-full" 
                  max="50" min="5" step="5" type="range" 
                  value={maxArticles}
                  onChange={(e) => setMaxArticles(Number(e.target.value))}
                />
            </div>

            {/* Advanced Options Accordion */}
            <div className="border border-outline-variant/50 rounded-[0.125rem] overflow-hidden">
              <input className="peer hidden" id="advanced-options-toggle" type="checkbox" />
              <label className="flex justify-between items-center p-4 cursor-pointer bg-surface/50 hover:bg-surface transition-colors select-none" htmlFor="advanced-options-toggle">
                <span className="font-[family-name:var(--font-inter)] text-[12px] text-on-surface uppercase tracking-widest font-semibold">Opsi Lanjutan</span>
                <span className="material-symbols-outlined text-outline transition-transform duration-300 peer-checked:rotate-180">expand_more</span>
              </label>
              
              <div className="hidden peer-checked:block border-t border-outline-variant/50 p-6 bg-white/50 space-y-8">
                <div className="text-[14px] text-on-surface-variant italic border-l-2 border-secondary-fixed-dim pl-3 py-1 mb-6">
                  Nilai optimal berbasis riset untuk peringkasan multi-dokumen ekstraktif telah dikonfigurasi sebelumnya. Menyesuaikan nilai ini memerlukan pemahaman tentang algoritma MMR (Maximal Marginal Relevance).
                </div>
                
                {/* Compression Rate Slider */}
                <div className="space-y-4">
                  <div className="flex justify-between items-end">
                    <label className="block font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold">Tingkat Kompresi</label>
                    <span className="font-[family-name:var(--font-inter)] text-[12px] text-primary-container font-semibold">{compression}%</span>
                  </div>
                  <input 
                    className="editorial-slider w-full" 
                    max="50" min="20" step="5" type="range" 
                    value={compression}
                    onChange={(e) => setCompression(Number(e.target.value))}
                  />
                  <div className="flex justify-between text-xs text-outline font-[family-name:var(--font-inter)]">
                    <span>20% (Padat)</span>
                    <span>50% (Ringan)</span>
                  </div>
                </div>

                {/* MMR Lambda Slider */}
                <div className="space-y-4">
                  <div className="flex justify-between items-end">
                    <label className="block font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold">Lambda MMR</label>
                    <span className="font-[family-name:var(--font-inter)] text-[12px] text-primary-container font-semibold">{lambda}</span>
                  </div>
                  <input 
                    className="editorial-slider w-full" 
                    max="0.9" min="0.1" step="0.1" type="range" 
                    value={lambda}
                    onChange={(e) => setLambda(Number(e.target.value))}
                  />
                  <div className="flex justify-between text-xs text-outline font-[family-name:var(--font-inter)]">
                    <span>0.1 (Keberagaman)</span>
                    <span>0.9 (Relevansi)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Submit Action */}
            <div className="pt-8">
              <button 
                onClick={handleSummarize}
                disabled={loading}
                className="w-full bg-primary-container text-on-primary py-4 px-6 rounded-[0.125rem] font-[family-name:var(--font-inter)] text-[12px] font-semibold uppercase tracking-widest hover:bg-primary transition-colors flex items-center justify-center gap-2 group" 
                type="button"
              >
                MULAI MERINGKAS
                <span className="material-symbols-outlined text-lg group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </>
  );
}
