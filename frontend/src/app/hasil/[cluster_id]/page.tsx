'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function DetailHasil() {
  const params = useParams();
  const router = useRouter();
  const clusterId = params.cluster_id;
  
  const [clusterData, setClusterData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const data = localStorage.getItem('berinkin_clusters');
    if (data) {
      const clusters = JSON.parse(data);
      // find the cluster by id or index
      const found = clusters.find((c: any, idx: number) => String(c.cluster_id) === String(clusterId) || String(idx) === String(clusterId));
      if (found) {
        setClusterData(found);
      } else {
        router.push('/hasil');
      }
    } else {
      router.push('/hasil');
    }
    setLoading(false);
  }, [clusterId, router]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Memuat ringkasan...</div>;
  }

  if (!clusterData) return null;

  return (
    <div className="px-4 sm:px-6 lg:px-8 max-w-[1200px] mx-auto w-full flex justify-center relative z-10 pt-4">
      <motion.article 
        initial={{ opacity: 0, y: 30 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="max-w-3xl w-full"
      >
        {/* Back Button */}
        <Link href="/hasil" className="inline-flex items-center gap-2 text-outline hover:text-primary mb-8 font-[family-name:var(--font-inter)] text-[14px] transition-colors group">
            <span className="material-symbols-outlined text-[18px] group-hover:-translate-x-1 transition-transform">arrow_back</span>
            Kembali ke Daftar Klaster
        </Link>

        {/* Article Header */}
        <header className="mb-12">
          <div className="flex items-center gap-4 mb-6">
            <span className="font-[family-name:var(--font-inter)] text-[12px] text-primary font-bold tracking-[0.2em] uppercase border-b-2 border-primary pb-1">
              KLASTER #{Number(clusterId) + 1}
            </span>
            <span className="text-outline px-2">•</span>
            <div className="flex items-center gap-1.5 text-[14px] font-[family-name:var(--font-inter)] text-on-surface-variant font-medium">
              <span className="material-symbols-outlined text-[16px]">article</span>
              {clusterData.article_count || clusterData.articles?.length} SUMBER
            </div>
            <span className="text-outline px-2">•</span>
            <span className="text-[12px] font-bold text-outline uppercase tracking-wider">Kompresi: {clusterData.compression_rate}%</span>
            <span className="text-outline px-2">•</span>
            <span className="text-[12px] font-bold text-outline uppercase tracking-wider">Lambda: {clusterData.lambda_value}</span>
          </div>
          <h1 className="text-[28px] sm:text-[36px] md:text-[42px] font-[family-name:var(--font-newsreader)] font-bold leading-[1.2] text-on-surface">
            {clusterData.topic_title}
          </h1>
        </header>

        {/* Article Body */}
        <div className="mb-16 max-w-[768px]">
          <div className="flex flex-col gap-6">
            {(clusterData.summary.match(/[^\.!\?]+[\.!\?]+/g) || [clusterData.summary]).reduce((result: string[], item: string, index: number) => {
              const chunkIndex = Math.floor(index / 3);
              if (!result[chunkIndex]) {
                result[chunkIndex] = '';
              }
              result[chunkIndex] += (result[chunkIndex] === '' ? '' : ' ') + item.trim();
              return result;
            }, []).map((paragraph: string, i: number) => (
              <p key={i} className="text-[17px] sm:text-[19px] font-[family-name:var(--font-inter)] leading-[1.8] text-on-surface-variant font-normal">
                {paragraph}
              </p>
            ))}
          </div>
        </div>

        {/* Source Articles Reference */}
        <div className="mb-12 border-t border-outline-variant/60 pt-8">
          <h3 className="font-[family-name:var(--font-inter)] text-[12px] text-on-surface-variant uppercase tracking-widest font-semibold mb-6">Daftar Sumber Referensi:</h3>
          <ul className="space-y-3">
            {clusterData.articles?.map((art: any, i: number) => (
              <li key={i} className="font-[family-name:var(--font-inter)] text-[14px] text-outline hover:text-primary transition-colors">
                <a href={art.url} target="_blank" rel="noopener noreferrer" className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-[16px] mt-0.5">link</span>
                  <span>{art.title}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Aesthetic Action Bar */}
        <div className="pt-8 border-t border-outline-variant/60 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="text-[14px] font-[family-name:var(--font-inter)] text-on-surface-variant">
            Dihasilkan oleh Pre-Trained SBERT Model
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <button className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full border border-outline-variant hover:border-primary/30 hover:bg-primary/5 transition-all text-on-surface-variant font-[family-name:var(--font-inter)] text-[14px] font-medium group">
              <span className="material-symbols-outlined text-[18px] text-on-surface-variant group-hover:text-primary transition-colors">content_copy</span>
              Salin
            </button>
            <button className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full bg-primary text-on-primary hover:bg-primary-container transition-colors font-[family-name:var(--font-inter)] text-[14px] font-medium shadow-sm">
              <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
              Ekspor PDF
            </button>
          </div>
        </div>
      </motion.article>
    </div>
  );
}
