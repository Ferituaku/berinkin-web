import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="w-full border-t-[0.5px] border-outline-variant bg-surface mt-20 pb-24 md:pb-0 relative overflow-hidden">
      {/* Decorative top border highlight */}
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary-fixed-dim to-transparent opacity-50"></div>
      
      <div className="max-w-[1200px] mx-auto px-10 py-16">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-12">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-sm border-[0.5px] border-primary flex items-center justify-center bg-primary-container relative">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-primary-fixed to-transparent opacity-30"></div>
                <div className="w-1.5 h-1.5 bg-on-primary-container rounded-full"></div>
              </div>
              <h3 className="font-[family-name:var(--font-newsreader)] text-2xl text-primary font-medium tracking-tight">
                Berinkin
              </h3>
            </div>
            <p className="font-[family-name:var(--font-inter)] text-sm text-on-surface-variant max-w-xs leading-relaxed font-light">
              Platform peringkasan berita harian otomatis, merangkum data yang terfragmentasi menjadi satu batang narasi berwibawa.
            </p>
          </div>
          
          <div className="flex gap-12 md:gap-16">
            
          </div>
        </div>
        
        <div className="mt-16 pt-8 border-t-[0.5px] border-outline-variant/50 flex flex-col-reverse md:flex-row justify-between items-start md:items-center gap-6 md:gap-0">
          <div className="font-[family-name:var(--font-inter)] text-xs text-outline flex items-center gap-2">
            <span>© {new Date().getFullYear()} Berinkin.</span>
            <span className="w-1 h-1 rounded-full bg-outline-variant"></span>
            <span>Berita Ringkas Terkini.</span>
          </div>
          
          <div className="font-[family-name:var(--font-inter)] text-xs text-outline flex items-center gap-1.5 px-3 py-1.5 rounded-full border-[0.5px] border-outline-variant/50 bg-surface-container-low">
            <span>Crafted with</span>
            <span className="material-symbols-outlined text-[14px] text-primary-container">psychiatry</span>
            <span>by <span className="font-medium text-primary">Ferro Putra</span></span>
          </div>
        </div>
      </div>
    </footer>
  );
}
