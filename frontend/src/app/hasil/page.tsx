'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function HasilKlaster() {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const data = localStorage.getItem('berinkin_clusters');
    if (data) {
      setClusters(JSON.parse(data));
    }
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Memuat...</div>;
  }

  if (clusters.length === 0) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center relative z-10">
        <span className="material-symbols-outlined text-[64px] text-outline-variant mb-4">hourglass_empty</span>
        <h2 className="font-[family-name:var(--font-newsreader)] text-2xl text-on-surface mb-2 font-medium">Belum ada hasil klasterisasi</h2>
        <p className="font-[family-name:var(--font-inter)] text-on-surface-variant mb-6 text-center max-w-md">Silakan kembali ke halaman Peringkas untuk mulai merangkum berita hari ini.</p>
        <Link href="/peringkas" className="px-6 py-3 bg-primary-container text-on-primary rounded-[0.125rem] font-[family-name:var(--font-inter)] text-[12px] uppercase tracking-widest font-semibold hover:bg-primary transition-colors">
          Mulai Meringkas
        </Link>
      </div>
    );
  }

  return (
    <main className="flex-grow w-full max-w-[1200px] mx-auto px-4 md:px-10 py-8 flex flex-col gap-12 relative z-10">
      {/* Header Section */}
      <section className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-[0.5px] border-outline-variant pb-8">
        <div className="flex flex-col gap-6">
          <motion.h1 
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
            className="font-[family-name:var(--font-newsreader)] text-[48px] leading-[1.1] text-primary-container font-semibold tracking-tight"
          >
            Hasil Klasterisasi
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}
            className="font-[family-name:var(--font-inter)] text-[18px] leading-[1.6] text-on-surface-variant max-w-2xl font-light"
          >
            Tinjauan komprehensif dari berbagai sumber informasi yang dikurasi dan diklasterisasi berdasarkan topik relevan.
          </motion.p>
        </div>
        <motion.button 
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.2 }}
          onClick={() => {
            if (confirm('Apakah Anda yakin ingin menghapus hasil klaster ini?')) {
              localStorage.removeItem('berinkin_clusters');
              setClusters([]);
            }
          }}
          className="px-4 py-2 border border-red-500 text-red-600 hover:bg-red-500 hover:text-white rounded-[0.125rem] font-[family-name:var(--font-inter)] text-[12px] uppercase tracking-widest font-semibold transition-colors flex items-center gap-2 self-start md:self-auto"
        >
          <span className="material-symbols-outlined text-[18px]">delete</span>
          Bersihkan Hasil
        </motion.button>
      </section>

      {/* Multi-Article Clusters */}
      {clusters.map((c: any, i: number) => ({ ...c, originalIdx: i })).filter((c: any) => (c.article_count || c.articles?.length || 0) > 1).length > 0 && (
        <div className="mb-12">
          <div className="flex items-center gap-4 mb-6">
            <h2 className="font-[family-name:var(--font-inter)] text-[14px] text-on-surface-variant uppercase tracking-[0.2em] font-bold">Klaster Terpadu</h2>
            <div className="h-[1px] bg-outline-variant flex-grow"></div>
          </div>
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {clusters.map((c: any, i: number) => ({ ...c, originalIdx: i })).filter((c: any) => (c.article_count || c.articles?.length || 0) > 1).map((cluster: any) => (
              <Link 
                key={cluster.originalIdx}
                href={`/hasil/${cluster.cluster_id !== undefined ? cluster.cluster_id : cluster.originalIdx}`} 
                className="group relative bg-white/80 backdrop-blur-[12px] border-[0.5px] border-outline-variant p-8 flex flex-col gap-6 hover:border-primary-container transition-colors cursor-pointer block"
              >
                <div className="absolute -top-[3px] -left-[3px] w-1.5 h-1.5 bg-primary-container"></div>
                <div className="absolute -top-[3px] -right-[3px] w-1.5 h-1.5 bg-primary-container"></div>
                <div className="absolute -bottom-[3px] -left-[3px] w-1.5 h-1.5 bg-primary-container"></div>
                <div className="absolute -bottom-[3px] -right-[3px] w-1.5 h-1.5 bg-primary-container"></div>

                <div className="flex justify-between items-center border-l-2 border-primary-container pl-3">
                  <span className="font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold">
                    KLASTER #{cluster.originalIdx + 1}
                  </span>
                  <div className="flex items-center gap-1 text-outline">
                    <span className="material-symbols-outlined text-[16px]">article</span>
                    <span className="font-[family-name:var(--font-inter)] text-[12px] font-semibold tracking-widest">{cluster.article_count || cluster.articles?.length || 0} SUMBER</span>
                  </div>
                </div>
                
                <div className="flex flex-col gap-3">
                  <h2 className="font-[family-name:var(--font-newsreader)] text-[24px] leading-[1.3] text-on-surface group-hover:text-primary-container transition-colors font-medium">
                    {cluster.topic_title}
                  </h2>
                  <div className="flex gap-2">
                     <span className="px-2 py-1 bg-surface-variant text-on-surface-variant text-[10px] uppercase font-bold rounded-sm tracking-wider">Kompresi: {cluster.compression_rate}%</span>
                     <span className="px-2 py-1 bg-surface-variant text-on-surface-variant text-[10px] uppercase font-bold rounded-sm tracking-wider">Lambda: {cluster.lambda_value}</span>
                  </div>
                  <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant line-clamp-3">
                    {cluster.summary}
                  </p>
                </div>
                
                <div className="mt-auto pt-4 border-t-[0.5px] border-surface-variant flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="font-[family-name:var(--font-inter)] text-[12px] text-primary-container uppercase tracking-widest font-semibold">Baca Ringkasan</span>
                  <span className="material-symbols-outlined text-primary-container">arrow_forward</span>
                </div>
              </Link>
            ))}
          </section>
        </div>
      )}

      {/* Single-Article Clusters */}
      {clusters.map((c: any, i: number) => ({ ...c, originalIdx: i })).filter((c: any) => (c.article_count || c.articles?.length || 0) <= 1).length > 0 && (
        <div>
          <div className="flex items-center gap-4 mb-6">
            <h2 className="font-[family-name:var(--font-inter)] text-[14px] text-on-surface-variant uppercase tracking-[0.2em] font-bold">Berita Tunggal</h2>
            <div className="h-[1px] bg-outline-variant flex-grow"></div>
          </div>
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-70 hover:opacity-100 transition-opacity">
            {clusters.map((c: any, i: number) => ({ ...c, originalIdx: i })).filter((c: any) => (c.article_count || c.articles?.length || 0) <= 1).map((cluster: any) => (
              <Link 
                key={cluster.originalIdx}
                href={`/hasil/${cluster.cluster_id !== undefined ? cluster.cluster_id : cluster.originalIdx}`} 
                className="group relative bg-surface/50 backdrop-blur-[12px] border-[0.5px] border-outline-variant p-8 flex flex-col gap-6 hover:border-outline transition-colors cursor-pointer block"
              >
                <div className="flex justify-between items-center border-l-2 border-outline-variant pl-3">
                  <span className="font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold">
                    BERITA #{cluster.originalIdx + 1}
                  </span>
                  <div className="flex items-center gap-1 text-outline">
                    <span className="material-symbols-outlined text-[16px]">article</span>
                    <span className="font-[family-name:var(--font-inter)] text-[12px] font-semibold tracking-widest">1 SUMBER</span>
                  </div>
                </div>
                
                <div className="flex flex-col gap-3">
                  <h2 className="font-[family-name:var(--font-newsreader)] text-[24px] leading-[1.3] text-on-surface group-hover:text-primary-container transition-colors font-medium">
                    {cluster.topic_title}
                  </h2>
                  <div className="flex gap-2">
                     <span className="px-2 py-1 bg-red-100 text-red-800 border border-red-200 text-[10px] uppercase font-bold rounded-sm tracking-wider">Tidak Teringkas</span>
                  </div>
                  <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant line-clamp-3">
                    {cluster.summary}
                  </p>
                </div>
                
                <div className="mt-auto pt-4 border-t-[0.5px] border-surface-variant flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="font-[family-name:var(--font-inter)] text-[12px] text-outline uppercase tracking-widest font-semibold">Lihat Detail</span>
                  <span className="material-symbols-outlined text-outline">arrow_forward</span>
                </div>
              </Link>
            ))}
          </section>
        </div>
      )}
    </main>
  );
}
