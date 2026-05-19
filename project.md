# Project Document: Berinkin (Berita Ringkasan Terkini)

## 1. Visi & Filosofi Produk
**Berinkin** adalah platform peringkasan berita harian multi-dokumen otomatis. Nama ini diambil dari filosofi **Pohon Beringin**:
- **Dedaunan & Cabang:** Merepresentasikan ribuan artikel berita mentah yang berserakan dan redundan.
- **Konvergensi:** Seperti cabang yang menyatu ke batang utama, Berinkin menyatukan berbagai artikel dengan topik yang sama menjadi satu ringkasan tunggal yang kokoh, akurat, dan esensial menggunakan algoritma MMR dan SBERT.

## 2. Spesifikasi Teknologi (Tech Stack)
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS.
- **Animation:** Framer Motion & GSAP (untuk transisi bertema "Convergence").
- **Backend:** FastAPI (Python 3.10+).
- **Database:** MySQL (Untuk manajemen riwayat/history ringkasan).
- **Object Storage:** Cloudflare R2 (S3-Compatible) – Untuk caching file JSON hasil crawling harian.
- **Machine Learning Core:**
    - Model SBERT: `paraphrase-multilingual-MiniLM-L12-v2` (Vektor 384-dimensi).
    - Clustering: `AgglomerativeClustering` (scikit-learn).
    - Selection Algorithm: `Maximal Marginal Relevance` (MMR).
- **Scraper:** `BeautifulSoup4` / `Newspaper3k`.

## 3. Arsitektur Data

### A. Cloudflare R2 (News Cache)
Menyimpan hasil crawling berita mentah untuk mencegah scraping berulang.
- **Path:** `buckets/news-cache/YYYY-MM-DD/{kategori}.json`
- **Format:** `[{"title": "...", "content": "...", "url": "..."}, ...]`

### B. MySQL Schema (Tabel `summary_history`)
Menyimpan hasil akhir ringkasan agar dapat diakses kembali secara instan.
```sql
CREATE TABLE summary_history (
    id VARCHAR(36) PRIMARY KEY,
    date_crawled DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    cluster_topic VARCHAR(255) NOT NULL,
    article_count INT DEFAULT 1,
    summary_text TEXT NOT NULL,
    compression_rate FLOAT DEFAULT 0.3,
    lambda_value FLOAT DEFAULT 0.7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

4. Pipeline Logic & Fitur Utama
Tahap 1: Discovery & Crawling
User memilih Tanggal dan Kategori (Bola, Tekno, Bisnis, Saham, Otomotif, Kesehatan).

Backend mengecek R2 Storage. Jika kosong, sistem melakukan crawling dan menyimpan hasilnya ke R2.

Tahap 2: Topic Clustering
Berita pada tanggal tersebut dikelompokkan menggunakan Agglomerative Hierarchical Clustering.

Hasil klaster ditampilkan di Frontend sebagai "Topik Berita Hari Ini".

Tahap 3: Peringkasan (The "Banyan" Logic)
Default Action: Tombol "Ringkas Sekarang" mengeksekusi parameter optimal dari riset: Kompresi 30% dan Lambda 0.7.

Advanced Options: Accordion tersembunyi untuk mengubah slider Kompresi (20%-50%) dan Lambda (0.1-0.9).

Processing: Menggunakan SBERT untuk embedding dan MMR untuk seleksi kalimat.

5. UI/UX & Branding (Editorial Minimalism)
Pelajari dan ikuti UI/UX yang sudah ada di file ui-reference. Jangan membuat UI dari awal.

6. Instruksi Implementasi Kritis (Consistency Guard)
PENTING: Untuk menjaga konsistensi hasil dengan penelitian skripsi:

Backend WAJIB merujuk pada file di folder reference/scrapper.py dan reference/peringkasan.ipynb.

Gunakan logika pembersihan teks, ekstraksi vektor SBERT, perhitungan Centroid, dan looping penalti MMR persis seperti yang ada pada file referensi tersebut.

Jangan melakukan improvisasi pada algoritma seleksi kalimat agar output teks tetap sama dengan hasil yang diuji pada skripsi.

7. Struktur Folder Project
/berinkin-app
├── /frontend (Next.js)
├── /backend (FastAPI)
│   ├── /core
│   │   ├── scraper.py (Adaptasi research code)
│   │   ├── summarizer.py (Adaptasi research code - SBERT & MMR)
│   ├── main.py
│   └── database.py
├── /reference
│   ├── scrapper.py (File Riset Asli)
│   └── peringkasan.ipynb (File Riset Asli)
├── /ui-reference
├── .env
└── project.md


