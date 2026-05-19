'use client';

import { motion, Variants } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import FallingLeaves from '@/components/FallingLeaves';

export default function Home() {
  const router = useRouter();
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  return (
    <motion.div 
      initial="hidden" 
      animate="visible" 
      variants={containerVariants}
      className="flex flex-col items-center"
    >
      <FallingLeaves />
      {/* Hero Section */}
      <motion.section variants={itemVariants} className="max-w-[1200px] mx-auto px-10 flex flex-col items-center text-center mt-12 mb-32 w-full">
        <div className="mb-8 relative w-24 h-24 mx-auto">
          <Image 
                            src="/banyan.png" 
                            alt="Berinkin Logo" 
                            fill 
                            sizes="96px"
                            className="object-contain opacity-90 mix-blend-multiply dark:mix-blend-normal"
                            priority
                          />
          <div className="absolute inset-0 -z-10 flex items-center justify-center opacity-20">
            <div className="w-[0.5px] h-32 bg-primary absolute"></div>
            <div className="w-[0.5px] h-32 bg-primary absolute rotate-45"></div>
            <div className="w-[0.5px] h-32 bg-primary absolute -rotate-45"></div>
          </div>
        </div>
        <h1 className="font-[family-name:var(--font-newsreader)] text-[48px] leading-[1.1] text-primary mb-6 max-w-4xl tracking-tight font-semibold">
          Berin' kin
        </h1>
        <p className="font-[family-name:var(--font-inter)] text-[18px] leading-[1.6] text-on-surface-variant max-w-2xl mb-12 font-light">
          Merangkum kekacauan data yang terfragmentasi menjadi satu ringkasan pengetahuan yang berwibawa.
        </p>
        <div className="relative group">
          <div className="absolute -inset-1 bg-primary blur-lg opacity-20 group-hover:opacity-40 transition duration-500 rounded-full"></div>
          <button className="relative bg-primary-container text-on-primary-container font-[family-name:var(--font-inter)] text-[12px] font-semibold uppercase px-8 py-4 rounded-full border-[0.5px] border-primary-fixed-dim hover:bg-primary transition-colors flex items-center gap-2 tracking-widest" onClick={() => router.push('/peringkas')}>
            <span >MULAI PERINGKASAN</span>
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </button>
        </div>
      </motion.section>

      {/* Introduction & Philosophy Section */}
      <motion.section variants={itemVariants} className="max-w-[1200px] mx-auto px-10 mb-40 w-full">
        <div className="relative bg-surface/80 backdrop-blur-xl border-[0.5px] border-outline-variant p-12 md:p-16">
          <div className="absolute -top-[2px] -left-[2px] w-[4px] h-[4px] bg-primary"></div>
          <div className="absolute -top-[2px] -right-[2px] w-[4px] h-[4px] bg-primary"></div>
          <div className="absolute -bottom-[2px] -left-[2px] w-[4px] h-[4px] bg-primary"></div>
          <div className="absolute -bottom-[2px] -right-[2px] w-[4px] h-[4px] bg-primary"></div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div>
              <div className="flex items-center gap-4 mb-6">
                <div className="w-8 h-[0.5px] bg-primary"></div>
                <span className="font-[family-name:var(--font-inter)] text-[12px] text-primary uppercase tracking-widest font-semibold">Filosofi</span>
              </div>
              <h2 className="font-[family-name:var(--font-newsreader)] text-[32px] leading-[1.2] text-on-surface mb-6 font-medium tracking-tight">Metafora Pohon Beringin</h2>
              <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant mb-6 font-normal">
                Di era kelebihan informasi, kejelasan adalah sebuah kemewahan. Sistem Berinkin terinspirasi oleh pohon Beringin—jaringan akar dan cabang yang kompleks yang pada akhirnya menyatu menjadi satu batang yang tak tergoyahkan.
              </p>
              <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant font-normal">
                Kami tidak sekadar mengumpulkan; kami merangkum. Dengan secara sistematis mengumpulkan narasi yang terfragmentasi di lanskap digital, kami menyintesisnya menjadi ringkasan yang padu dan berketepatan tinggi yang menghargai waktu dan kecerdasan Anda.
              </p>
            </div>
            <div className="relative h-64 md:h-full min-h-[300px] border-[0.5px] border-outline-variant overflow-hidden bg-surface-container-low">
              <img alt="Abstract depiction of summarization" className="w-full h-full object-cover mix-blend-luminosity opacity-80" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDGHNRk82u_VZeYocserLt6qeQoWuKBf7tYIw_bPFMpgJufUUn4ZY8e5NU6RWQI3EH-jyCgZeB1BknXDhuzHIR_GNS4U8J_WfdIrPVBOwC4HjdD4ks9xXT4BRJOTwkJy8T1nAVV94piVfVuks9QcXNxrSNdUe5HtaHbFGW7FbNLsVUftPsCCT8Y-SH41w3Hak2uMHpcenNNI-xnP5w17j4WHfVUP9UMM4bKh_9Ox0jy1yX8427j5N9Q11zuZaUzypWcZFdCRBNhM18"/>
              <div className="absolute inset-0 bg-gradient-to-t from-surface to-transparent opacity-50"></div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Technical Pipeline Section */}
      <motion.section variants={itemVariants} className="max-w-[1200px] mx-auto px-10 mb-32 w-full">
        <div className="text-center mb-16">
          <h2 className="font-[family-name:var(--font-newsreader)] text-[32px] leading-[1.2] text-on-surface mb-4 font-medium tracking-tight">Alur Peringkasan</h2>
          <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant">Sebuah metodologi empat langkah yang ketat untuk peringkasan informasi.</p>
        </div>
        
        <div className="relative max-w-4xl mx-auto pl-0">
          <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-[0.5px] bg-outline-variant -translate-x-1/2"></div>
          
          {/* Step 1 */}
          <motion.div initial={{ opacity: 0, x: -50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }} className="relative flex flex-col md:flex-row items-start md:items-center justify-between mb-24 group">
            <div className="absolute left-6 md:left-1/2 w-4 h-4 bg-background border-[0.5px] border-primary rotate-45 -translate-x-1/2 mt-6 md:mt-0 flex items-center justify-center z-10">
              <div className="w-1.5 h-1.5 bg-primary group-hover:bg-primary-container transition-colors"></div>
            </div>
            <div className="w-full md:w-5/12 pl-16 md:pl-0 text-left md:text-right pr-0 md:pr-12">
              <span className="font-[family-name:var(--font-inter)] text-[12px] text-outline mb-2 block font-semibold tracking-widest">FASE 01</span>
              <h3 className="font-[family-name:var(--font-newsreader)] text-[24px] leading-[1.3] text-on-surface mb-3 font-medium">Pengambilan Berita</h3>
              <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant">Ekstraksi sistematis data mentah dan terfragmentasi dari portal resmi di seluruh jaringan.</p>
            </div>
            <div className="hidden md:flex md:w-5/12 pl-12 items-center justify-start">
              <div className="w-full h-32 border-[0.5px] border-outline-variant bg-surface/50 backdrop-blur-sm relative flex items-center justify-center">
                <span className="material-symbols-outlined text-[40px] text-primary opacity-80">travel_explore</span>
              </div>
            </div>
          </motion.div>

          {/* Step 2 */}
          <motion.div initial={{ opacity: 0, x: 50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }} className="relative flex flex-col md:flex-row items-start md:items-center justify-between mb-24 md:flex-row-reverse group">
            <div className="absolute left-6 md:left-1/2 w-4 h-4 bg-background border-[0.5px] border-primary rotate-45 -translate-x-1/2 mt-6 md:mt-0 flex items-center justify-center z-10">
              <div className="w-1.5 h-1.5 bg-primary group-hover:bg-primary-container transition-colors"></div>
            </div>
            <div className="hidden md:flex md:w-5/12 pr-12 items-center justify-end">
              <div className="w-full h-32 border-[0.5px] border-outline-variant bg-surface/50 backdrop-blur-sm relative flex items-center justify-center">
                <span className="material-symbols-outlined text-[40px] text-primary opacity-80">hub</span>
              </div>
            </div>
            <div className="w-full md:w-5/12 pl-16 md:pl-12 text-left">
              <span className="font-[family-name:var(--font-inter)] text-[12px] text-outline mb-2 block font-semibold tracking-widest">FASE 02</span>
              <h3 className="font-[family-name:var(--font-newsreader)] text-[24px] leading-[1.3] text-on-surface mb-3 font-medium">Pengelompokan Topik</h3>
              <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant">Pengelompokan algoritmik dari kesamaan semantik, memastikan beragam perspektif disejajarkan ke dalam topik-topik terpisah.</p>
            </div>
          </motion.div>

          {/* Step 3 */}
          <motion.div initial={{ opacity: 0, x: -50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }} className="relative flex flex-col md:flex-row items-start md:items-center justify-between mb-24 group">
            <div className="absolute left-6 md:left-1/2 w-4 h-4 bg-background border-[0.5px] border-primary rotate-45 -translate-x-1/2 mt-6 md:mt-0 flex items-center justify-center z-10">
              <div className="w-1.5 h-1.5 bg-primary group-hover:bg-primary-container transition-colors"></div>
            </div>
            <div className="w-full md:w-5/12 pl-16 md:pl-0 text-left md:text-right pr-0 md:pr-12">
              <span className="font-[family-name:var(--font-inter)] text-[12px] text-outline mb-2 block font-semibold tracking-widest">FASE 03</span>
              <h3 className="font-[family-name:var(--font-newsreader)] text-[24px] leading-[1.3] text-on-surface mb-3 font-medium">Peringkasan BERT &amp; MMR</h3>
              <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant">Penyematan semantik mendalam dipadukan dengan Maximal Marginal Relevance untuk mengekstrak informasi yang paling menonjol dan tidak berlebihan.</p>
            </div>
            <div className="hidden md:flex md:w-5/12 pl-12 items-center justify-start">
              <div className="w-full h-32 border-[0.5px] border-outline-variant bg-surface/50 backdrop-blur-sm relative flex items-center justify-center">
                <span className="material-symbols-outlined text-[40px] text-primary opacity-80">compress</span>
              </div>
            </div>
          </motion.div>

          {/* Step 4 */}
          <motion.div initial={{ opacity: 0, x: 50 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-100px" }} transition={{ duration: 0.8 }} className="relative flex flex-col md:flex-row items-start md:items-center justify-between md:flex-row-reverse group">
            <div className="absolute left-6 md:left-1/2 w-4 h-4 bg-background border-[0.5px] border-primary rotate-45 -translate-x-1/2 mt-6 md:mt-0 flex items-center justify-center z-10">
              <div className="w-2 h-2 bg-primary group-hover:bg-primary-container transition-colors"></div>
            </div>
            <div className="hidden md:flex md:w-5/12 pr-12 items-center justify-end">
              <div className="w-full h-32 bg-surface border-[0.5px] border-primary relative flex items-center justify-center">
                <div className="absolute -top-[2px] -left-[2px] w-[4px] h-[4px] bg-primary"></div>
                <div className="absolute -top-[2px] -right-[2px] w-[4px] h-[4px] bg-primary"></div>
                <div className="absolute -bottom-[2px] -left-[2px] w-[4px] h-[4px] bg-primary"></div>
                <div className="absolute -bottom-[2px] -right-[2px] w-[4px] h-[4px] bg-primary"></div>
                <div className="flex flex-col items-center gap-2">
                  <span className="material-symbols-outlined text-[40px] text-primary">task_alt</span>
                  <span className="text-primary font-[family-name:var(--font-newsreader)] text-[24px] font-medium">
                    Peringkasan
                  </span>
                </div>
              </div>
            </div>
            <div className="w-full md:w-5/12 pl-16 md:pl-12 text-left">
              <span className="font-[family-name:var(--font-inter)] text-[12px] text-outline mb-2 block font-semibold tracking-widest">FASE 04</span>
              <h3 className="font-[family-name:var(--font-newsreader)] text-[24px] leading-[1.3] text-on-surface mb-3 font-medium">Hasil Ringkasan</h3>
              <p className="font-[family-name:var(--font-inter)] text-[16px] leading-[1.5] text-on-surface-variant">Keluaran akhir: batang narasi otoritatif yang dirangkum tanpa kebisingan dan pengulangan.</p>
            </div>
          </motion.div>
        </div>
      </motion.section>
    </motion.div>
  );
}
