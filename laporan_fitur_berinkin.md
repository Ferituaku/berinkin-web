# Daftar Panduan Tangkapan Layar (Screenshot) Fitur Berinkin untuk Laporan

Dokumen ini berisi daftar fitur utama pada aplikasi **Berinkin** beserta deskripsi singkatnya. Gunakan daftar ini sebagai panduan untuk mengambil tangkapan layar (*screenshot*) dan menyusun laporan skripsi atau dokumentasi sistem Anda.

---

## 1. Halaman Utama (Landing Page)

Halaman ini berfungsi sebagai pintu gerbang utama yang menyambut pengguna dan menjelaskan identitas serta metodologi sistem Berinkin.

- **[CAPTURE SCREEN 1: Hero Section]**
  - **Deskripsi:** Menampilkan logo beringin, judul aplikasi, dan *tagline* utama. Terdapat animasi interaktif berupa dedaunan beringin yang berguguran dan merespons pergerakan kursor (*mouse*), serta tombol "Mulai Peringkasan" untuk masuk ke sistem utama.
  
- **[CAPTURE SCREEN 2: Filosofi Sistem]**
  - **Deskripsi:** Bagian yang menjelaskan metafora Pohon Beringin yang menjadi dasar filosofi sistem—menggambarkan bagaimana jaringan informasi yang kompleks disintesis menjadi satu batang narasi utama yang kokoh.

- **[CAPTURE SCREEN 3: Alur Peringkasan (Pipeline)]**
  - **Deskripsi:** Menampilkan infografis metodologi empat langkah algoritma: (1) Pengambilan Berita, (2) Pengelompokan Topik, (3) Peringkasan BERT & MMR, dan (4) Hasil Ringkasan, yang dilengkapi dengan ikon representatif.

- **[CAPTURE SCREEN 4: Footer Premium]**
  - **Deskripsi:** Bagian bawah halaman yang memuat informasi *copyright*, navigasi tautan, dan kredit nama pembuat aplikasi ("Crafted with 🌿 by Ferro Putra").

---

## 2. Halaman Peringkas (Konfigurasi Ekstraksi)

Halaman ini adalah pusat kontrol (*dashboard*) bagi pengguna untuk menentukan parameter pengambilan dan peringkasan berita.

- **[CAPTURE SCREEN 5: Form Parameter Dasar]**
  - **Deskripsi:** Menampilkan *dropdown* untuk memilih Kategori Berita (Teknologi, Ekonomi, dll), input Tanggal Berita, serta *slider* untuk menentukan Target Jumlah Berita yang akan di-crawling.

- **[CAPTURE SCREEN 6: Opsi Lanjutan (Advanced Options)]**
  - **Deskripsi:** Menampilkan *slider* parameter algoritma. Terdapat pengaturan "Tingkat Kompresi" (20% - 50%) untuk mengatur kepadatan/jumlah kalimat ringkasan, dan "Lambda MMR" (0.1 - 0.9) untuk mengatur keseimbangan antara relevansi dan keberagaman kalimat.

- **[CAPTURE SCREEN 7: Loading Overlay (Proses Ekstraksi)]**
  - **Deskripsi:** Tampilan saat tombol "Mulai Meringkas" ditekan. Menampilkan *progress bar* interaktif berupa persentase dan teks status dari sistem *backend* secara *real-time* (SSE) seperti "Mengekstraksi vektor...", dengan latar belakang efek *glassmorphism*.

---

## 3. Halaman Daftar Hasil Klasterisasi

Halaman ini menampilkan seluruh topik yang berhasil diekstraksi dan dikelompokkan oleh algoritma *Agglomerative Clustering* pada hari tersebut.

- **[CAPTURE SCREEN 8: Daftar Klaster Terpadu]**
  - **Deskripsi:** Menampilkan *grid* kartu (*card*) dari topik-topik berita yang terbentuk dari gabungan beberapa artikel (*multi-document*). Setiap kartu memuat judul topik, cuplikan ringkasan, jumlah sumber berita, serta parameter (Kompresi & Lambda) yang digunakan.

- **[CAPTURE SCREEN 9: Berita Tunggal (Outliers)]**
  - **Deskripsi:** Menampilkan daftar artikel yang tidak memiliki kesamaan semantik dengan berita lain, sehingga tidak dikelompokkan dan tidak diringkas secara ekstensif.

---

## 4. Halaman Detail Ringkasan Topik

Halaman ini adalah hasil akhir berupa *executive summary* dari suatu klaster/topik berita yang dipilih pengguna.

- **[CAPTURE SCREEN 10: Header Detail Topik]**
  - **Deskripsi:** Menampilkan judul besar dari topik berita yang diringkas, beserta metadata sistem (Label Klaster, Jumlah Sumber, nilai Kompresi, dan nilai Lambda).

- **[CAPTURE SCREEN 11: Teks Hasil Ringkasan]**
  - **Deskripsi:** Menampilkan paragraf-paragraf hasil ekstraksi kalimat terbaik (Top-N sentences) oleh algoritma SBERT & MMR. Teks disajikan dengan tipografi yang bersih, margin yang proporsional, dan terbagi ke dalam paragraf pendek agar nyaman dibaca.

- **[CAPTURE SCREEN 12: Daftar Sumber Referensi]**
  - **Deskripsi:** Menampilkan daftar tautan (*hyperlink*) menuju artikel berita asli yang digunakan oleh sistem untuk menyusun ringkasan pada topik tersebut, sebagai bentuk transparansi dan verifikasi informasi.

- **[CAPTURE SCREEN 13: Action Bar (Tombol Aksi)]**
  - **Deskripsi:** Menampilkan tombol interaktif di bagian bawah halaman untuk fungsi utilitas, yaitu "Salin" teks ringkasan ke *clipboard* dan fitur "Ekspor PDF" (jika diimplementasikan).
