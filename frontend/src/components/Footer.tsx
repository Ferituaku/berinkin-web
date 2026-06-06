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
                Berin'kin
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
            <span>© {new Date().getFullYear()} Berin'kin.</span>
            <span className="w-1 h-1 rounded-full bg-outline-variant"></span>
            <span>Berita Ringkas Terkini.</span>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="https://github.com/Ferituaku/berinkin-web"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-8 h-8 rounded-full border-[0.5px] border-outline-variant/50 bg-surface-container-low hover:border-primary-fixed-dim hover:bg-primary/5 transition-all text-outline hover:text-primary"
              title="View Source Code on GitHub"
            >
              <svg
                className="w-4 h-4"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  clipRule="evenodd"
                  d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.167 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.164 22 16.418 22 12c0-5.523-4.477-10-10-10z"
                />
              </svg>
            </Link>

            <div className="font-[family-name:var(--font-inter)] text-xs text-outline flex items-center gap-1.5 px-3 py-1.5 rounded-full border-[0.5px] border-outline-variant/50 bg-surface-container-low">
              <span>Crafted with</span>
              <span className="material-symbols-outlined text-[14px] text-primary-container">psychiatry</span>
              <span>by <span className="font-medium text-primary">Ferro Putra</span></span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
