!pip install transformers sentence-transformers torch scikit-learn Sastrawi nltk protobuf sentencepiece pandas

import os
import json
import re
import numpy as np
import torch
import logging
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import nltk
nltk.download('punkt')
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from transformers import AutoTokenizer,AutoModel, AutoModelForSeq2SeqLM, MBartTokenizer, BertTokenizer
from sentence_transformers import SentenceTransformer
from google.colab import drive

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

class TextPreprocessor:
    def __init__(self):
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()

    def clean_text_display(self, text: str) -> str:
        # PEMBERSIHAN KHUSUS TAMPILAN

        remove = [r'^liputan6\.com\s*(?:-|:)\s*',r'^(?:liputan6\.com|com)\s*,\s*[a-z\s]+\s*(?:-|:)\s*',r'BACA JUGA:.*?(?=\n|$)', r'Disclaimer:.*?(?=\n|$)', r'^\s*ADVERTISEMENT.*?(?=\n|$)',
                  r'Perbesar', r'Selengkapnya', r'\d+\s+dari\s+\d+\s+halaman', r'\s*\([A-Za-z0-9/\.\s-]+\)\.?\s*$']
        for p in remove: text = re.sub(p, ' ', text, flags=re.IGNORECASE|re.DOTALL)

        # Fix Spasi Gancet
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', text)
        text = re.sub(r'([.,!?])(?=[a-zA-Z])', r'\1 ', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
        text = text.encode('ascii', 'ignore').decode('ascii')

        return re.sub(r'\s+', ' ', text).strip()

    def case_folding_and_remove_artifacts(self, text: str) -> str:
        # TAHAP 3 & 4: CASE FOLDING & CLEANING KOMPUTASI
        text = text.lower()
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'[^a-z\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def split_sentences(self, text: str) -> List[str]:
        try: return sent_tokenize(text)
        except: return re.split(r'(?<=[.!?])\s+', text)
class SentenceBERTEmbedder:
    """
    Sentence-BERT (SBERT) paraphrase-multilingual-MiniLM-L12-v2 (Support Bahasa Indonesia)
    """
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        print(f"   [Model] Loading Sentence-BERT ({model_name})...")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        try:
            self.model = SentenceTransformer(model_name, device=str(self.device))
        except Exception as e:
            print(f"  Gagal load SBERT: {e}")
            raise

    def get_embeddings(self, sentences: List[str]):
        if not sentences: return np.array([])
        embeddings = self.model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
        return embeddings
# import numpy as np
# import pandas as pd
# from dataclasses import dataclass
# from typing import List, Optional

# @dataclass
# class Article:
#     url: str; title: str; content: str; category: str
#     date: Optional[str] = None; author: Optional[str] = None; tags: List[str] = None

# class MMRSelector:
#     def __init__(self, lambda_param=0.7):
#         self.lambda_param = lambda_param

#     def _cosine_similarity(self, A, B):
#         """
#         Rumus: (A . B) / (||A|| * ||B||)
#         """
#         dot_product = np.dot(A, B.T)
#         norm_a = np.linalg.norm(A, axis=1, keepdims=True)
#         norm_b = np.linalg.norm(B, axis=1, keepdims=True)
#         denominator = np.dot(norm_a, norm_b.T) + 1e-10
#         return dot_product / denominator

#     def select_with_logs(self, sentences_data, embs, query, n=5):
#         if not sentences_data: return [], [], []

#         embs = np.array(embs)
#         query = np.array(query)
#         if query.ndim == 1: query = query.reshape(1, -1)
#         if embs.ndim == 1: embs = embs.reshape(1, -1)

#         # 1. HITUNG RELEVANSI MURNI (SIM_1)
#         sim_to_query = self._cosine_similarity(embs, query).flatten()
#         raw_sim_to_query = sim_to_query.copy()

#         heuristic_logs = []

#         # 2. MODIFIKASI HEURISTIK (STATE TRACKER + 50% & 30% BOOST)
#         doc_quote_state = {}

#         for i, item in enumerate(sentences_data):
#             text = item['text'].lower() if isinstance(item, dict) else str(item).lower()

#             # Ambil identitas dokumen & urutan kalimatnya
#             doc_id = item.get('doc_id', 'unknown')
#             sent_id = item.get('sent_id', i)

#             if doc_id not in doc_quote_state:
#                 doc_quote_state[doc_id] = False

#             was_in_quote = doc_quote_state[doc_id]

#             straight_quotes = text.count('"')
#             has_curly_open = '“' in text
#             has_curly_close = '”' in text

#             rule_notes = []
#             multiplier = 1.0

#             # Quote Penalty Tracker
#             is_penalized = was_in_quote or (straight_quotes > 0) or has_curly_open or has_curly_close

#             if is_penalized:
#                 multiplier *= 0.70
#                 rule_notes.append("Quote Penalty (*0.70)")

#             # Update State Kutipan
#             if has_curly_open and not has_curly_close:
#                 doc_quote_state[doc_id] = True
#             elif has_curly_close and not has_curly_open:
#                 doc_quote_state[doc_id] = False
#             elif straight_quotes % 2 != 0:
#                 doc_quote_state[doc_id] = not doc_quote_state[doc_id]

#             # Position Boost 50% dan 30%
#             if sent_id == 1:
#                 multiplier *= 1.3
#                 rule_notes.append("Position Boost 2 (*1.30)")

#             sim_to_query[i] *= multiplier
#             applied_rule = " + ".join(rule_notes) if rule_notes else "Normal"

#             heuristic_logs.append({
#                 "Doc ID": doc_id,
#                 "Sent ID": sent_id,
#                 "Raw Sim_1": float(raw_sim_to_query[i]),
#                 "Multiplier": multiplier,
#                 "Modified Sim_1": float(sim_to_query[i]),
#                 "Rule Applied": applied_rule,
#                 "Text Snippet": text[:1000]
#             })

#         sel_idx = []
#         rem_idx = list(range(len(sentences_data)))
#         logs = []

#         # 3. LOOP MMR
#         while len(sel_idx) < n and rem_idx:
#             step_candidates = []

#             if sel_idx:
#                 selected_vecs = embs[sel_idx]

#             for i in rem_idx:
#                 rel = sim_to_query[i]
#                 div = 0.0
#                 if sel_idx:
#                     curr_vec = embs[i].reshape(1, -1)
#                     sim_to_selected = self._cosine_similarity(curr_vec, selected_vecs)
#                     div = np.max(sim_to_selected)

#                 score = self.lambda_param * rel - (1 - self.lambda_param) * div

#                 step_candidates.append({
#                     "idx": i, "score": score, "rel": rel, "div": div
#                 })

#             best = max(step_candidates, key=lambda x: x['score'])

#             sel_idx.append(best['idx'])
#             rem_idx.remove(best['idx'])
#             s = sentences_data[best['idx']]

#             doc_id = s.get('doc_id', '?')
#             sent_id = s.get('sent_id', '?')
#             source_str = f"[doc_{doc_id}, sent_{sent_id}]"

#             logs.append({
#                 "Step": len(sel_idx),
#                 "Source": source_str,
#                 "MMR Score": float(best['score']),
#                 "Modified Sim_1 (Rel)": float(best['rel']),
#                 "Diversity": float(best['div']),
#                 "Text": s['text'][:1000]
#             })

#         # sel_idx
#         selected_final = [sentences_data[i] for i in sel_idx]

#         return selected_final, logs, heuristic_logs
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional

class Article:
    url: str; title: str; content: str; category: str
    date: Optional[str] = None; author: Optional[str] = None; tags: List[str] = None

class MMRSelector:
    def __init__(self, lambda_param=0.7):
        self.lambda_param = lambda_param

    def _cosine_similarity(self, A, B):
        """
        Rumus: (A . B) / (||A|| * ||B||)
        """
        dot_product = np.dot(A, B.T)
        norm_a = np.linalg.norm(A, axis=1, keepdims=True)
        norm_b = np.linalg.norm(B, axis=1, keepdims=True)
        denominator = np.dot(norm_a, norm_b.T) + 1e-10
        return dot_product / denominator

    def select_with_logs(self, sentences_data, embs, query, n=5):
        if not sentences_data: return [], [], []

        embs = np.array(embs)
        query = np.array(query)
        if query.ndim == 1: query = query.reshape(1, -1)
        if embs.ndim == 1: embs = embs.reshape(1, -1)

        # 1. HITUNG RELEVANSI MURNI (SIM_1)
        sim_to_query = self._cosine_similarity(embs, query).flatten()

        heuristic_logs = []

        # 2. LOGGING BASELINE (Tanpa Modifikasi Heuristik)
        for i, item in enumerate(sentences_data):
            text = item['text'].lower() if isinstance(item, dict) else str(item).lower()

            # Ambil identitas dokumen & urutan kalimatnya
            doc_id = item.get('doc_id', 'unknown')
            sent_id = item.get('sent_id', i)

            # BASELINE: Multiplier selalu 1.0 (Skor murni SBERT)
            multiplier = 1.0

            heuristic_logs.append({
                "Doc ID": doc_id,
                "Sent ID": sent_id,
                "Raw Sim_1": float(sim_to_query[i]),
                "Multiplier": multiplier,
                "Modified Sim_1": float(sim_to_query[i]),
                "Rule Applied": "Baseline (Normal)",
                "Text Snippet": text[:1000]
            })

        sel_idx = []
        rem_idx = list(range(len(sentences_data)))
        logs = []

        # 3. LOOP MMR
        while len(sel_idx) < n and rem_idx:
            step_candidates = []

            if sel_idx:
                selected_vecs = embs[sel_idx]

            for i in rem_idx:
                rel = sim_to_query[i]
                div = 0.0
                if sel_idx:
                    curr_vec = embs[i].reshape(1, -1)
                    sim_to_selected = self._cosine_similarity(curr_vec, selected_vecs)
                    div = np.max(sim_to_selected)

                score = self.lambda_param * rel - (1 - self.lambda_param) * div

                step_candidates.append({
                    "idx": i, "score": score, "rel": rel, "div": div
                })

            best = max(step_candidates, key=lambda x: x['score'])

            sel_idx.append(best['idx'])
            rem_idx.remove(best['idx'])
            s = sentences_data[best['idx']]

            doc_id = s.get('doc_id', '?')
            sent_id = s.get('sent_id', '?')
            source_str = f"[doc_{doc_id}, sent_{sent_id}]"

            logs.append({
                "Step": len(sel_idx),
                "Source": source_str,
                "MMR Score": float(best['score']),
                "Modified Sim_1 (Rel)": float(best['rel']),
                "Diversity": float(best['div']),
                "Text": s['text'][:1000]
            })

        # sel_idx.sort()
        selected_final = [sentences_data[i] for i in sel_idx]

        return selected_final, logs, heuristic_logs
print("⏳ Menginisialisasi Model...")
preprocessor = TextPreprocessor()
embedder = SentenceBERTEmbedder()
mmr = MMRSelector()
vectorizer = TfidfVectorizer(max_features=1000)
print(" Model Siap.\n")
import os
import shutil
from google.colab import drive

os.system('fusermount -uz /content/drive')

if os.path.isdir('/content/drive') and os.listdir('/content/drive'):
    print("Warning: /content/drive still contains files after fusermount. Attempting to force clear.")
    try:
        shutil.rmtree('/content/drive')
        os.makedirs('/content/drive')
        print("/content/drive successfully removed and recreated.")
    except Exception as e:
        print(f"Error forcibly clearing /content/drive: {e}")

drive.mount('/content/drive', force_remount=True)

RAW_DATA_PATH = "/content/drive/MyDrive/Skripsi-Multi-Documents-Summary/data/raw/liputan6"
CATEGORY = "tekno" # custom kategori
CLUSTERING_THRESHOLD = 0.8
import pandas as pd

print("\nLoad judul artikel")
cat_dir = os.path.join(RAW_DATA_PATH, CATEGORY)
articles, raw_docs = [], []

if os.path.exists(cat_dir):
    for f in os.listdir(cat_dir):
        if f.endswith('.json'):
            try:
                d = json.load(open(os.path.join(cat_dir, f)))
                feat = f"{d['title']} {d['title']} {d.get('content','')[:500]}"
                articles.append(feat)
                raw_docs.append(d)
            except Exception as e:
                print(f"Skipping error file {f}: {e}")

if not articles: print("Data kosong"); exit()
vecs = vectorizer.fit_transform(articles).toarray()
# 2. CLUSTERING
clusterer = AgglomerativeClustering(
    n_clusters=None,
    metric='cosine',
    linkage='average',
    distance_threshold=CLUSTERING_THRESHOLD
)
labels = clusterer.fit_predict(vecs)
# 3. GROUPING
clusters_dict = {}
for i, lbl in enumerate(labels):
    if lbl not in clusters_dict: clusters_dict[lbl] = []
    clusters_dict[lbl].append(raw_docs[i])
#visualisasi cluster
print("PENGELOMPOKAN DOKUMEN (CLUSTERING)")
print("="*80)

clusters_list = []
valid_idx_counter = 0

sorted_lbls = sorted(clusters_dict.keys())
for lbl in sorted_lbls:
    docs = clusters_dict[lbl]
    is_valid = len(docs) >= 2

    if is_valid:
        status_icon = "VALID"
        clusters_list.append(docs)

        current_list_index = valid_idx_counter
        valid_idx_counter += 1

        index_msg = f"TARGET_INDEX = {current_list_index}"
    else:
        status_icon = "SKIP (Artikel < 2)"
        index_msg = "(Tidak masuk list analisis)"

    # Visualisasi Header
    status_icon = " VALID (Proses ke Summarization)" if is_valid else " SKIP (Artikel Tunggal/Kurang)"
    print(f"\n CLUSTER ID: {lbl}")
    print(f"   STATUS: {status_icon}")
    print(f"   JUMLAH ARTIKEL: {len(docs)}")
    print(f"   {index_msg}")
    print("   " + "-"*60)

    # List Judul
    for k, doc in enumerate(docs):
        print(f"   {k+1}. {doc['title']}")

    print("   " + "-"*60)

print("\n" + "="*85)
print(f" Total Klaster Valid tersimpan di 'clusters_list': {len(clusters_list)}")
print("="*85 + "\n")
# @title Konfigurasi & Load Target Klaster
import pandas as pd
import numpy as np
import re

pd.set_option('display.max_colwidth', None)

# --- KONFIGURASI ---
USE_STEMMING = False
TARGET_CLUSTER_INDEX = 2


if not clusters_list:
    raise ValueError(" Error: Tidak ada klaster yang tersedia di 'clusters_list'!")

target_cluster = clusters_list[TARGET_CLUSTER_INDEX]

print(f"Klaster Topik Index [{TARGET_CLUSTER_INDEX}]")
print(f"Judul Utama: '{target_cluster[0]['title'][:500]}.'")
print(f"Jumlah Artikel dalam Klaster: {len(target_cluster)}")
print(f"Mode Stemming aktif: {USE_STEMMING}")
#text cleaning & Sentence Splitting
print("[Processing] Memulai Preprocessing...\n")

preprocessor = TextPreprocessor()
all_data = []

for doc_idx, art in enumerate(target_cluster):
    original_text = art['content']

    clean_display = preprocessor.clean_text_display(original_text)

    sents = preprocessor.split_sentences(clean_display)

    print("="*60)
    print(f"🔍 DEMO TAHAPAN PREPROCESSING (DOKUMEN {doc_idx + 1})")
    print("="*60)
    print(f"🟢 1. TEKS MENTAH AWAL:\n{original_text[:1000000]}...\n")
    print(f"🟢 2. HASIL TAHAP 1 - DISPLAY CLEANSING:\n{clean_display[:1000000]}...\n")


    print(f"🟢 3. HASIL TAHAP 2 - SENTENCE SPLITTING (3 Kalimat Pertama):")
    for i, s in enumerate(sents[:3]):
        print(f"   [{i+1}] {s}")

    print(f"\n🟢 4. HASIL TAHAP 3 - LENGTH FILTERING & CASE FOLDING:")

    for sent_idx, s in enumerate(sents):
        s = s.strip()

        if len(s) >= 20 and re.search(r'[a-zA-Z]', s):

            calc_text = preprocessor.case_folding_and_remove_artifacts(s)

            if sent_idx < 3:
                print(f"   [Valid] -> {calc_text}")

            # Simpan ke memori
            meta = {
                'doc_id': doc_idx + 1,
                'sent_id': sent_idx + 1,
                'original_text': s,      # Teks ini untuk ditampilkan di ringkasan akhir
                'calc_text': calc_text   # Teks ini yang akan dikonversi SBERT
            }
            all_data.append(meta)

        else:
            if sent_idx < 3:
                print(f"   [Dibuang (Noise/Terlalu Pendek)] -> {s}")

    print("="*60, "\n")

print(f"✅ Preprocessing Selesai untuk seluruh dokumen.")
print(f"✅ Total Kalimat Valid: {len(all_data)} kalimat\n")

# Menampilkan hasil akhir DataFrame
print("📊 Sample Data Tersimpan (Format Input SBERT):")
df_prep = pd.DataFrame(all_data)[['doc_id', 'sent_id', 'original_text', 'calc_text']]
df_prep.columns = ['Doc ID', 'Sent ID', 'Kalimat Asli (Tampilan)', 'Kalimat Bersih (Input SBERT)']

# Menampilkan 10 baris pertama di tabel. Ubah head(10) menjadi display(df_prep) jika ingin melihat semua baris.
display(df_prep.head(10))
#text celaning & Sentence Splitting
print("[Processing]...")

all_data = []
calc_texts = []   # (clean/stemmed teks)

for doc_idx, art in enumerate(target_cluster):

    clean = preprocessor.clean_text_display(art['content'])

    sents = preprocessor.split_sentences(clean)

    for sent_idx, s in enumerate(sents):
        s = s.strip()
        if len(s) >= 20 and re.search(r'[a-zA-Z]', s):
            clean_artifact_text = preprocessor.case_folding_and_remove_artifacts(s)
            if USE_STEMMING:
                processed = preprocessor.stemming_process(clean_artifact_text)
            else:
                processed = clean_artifact_text

            meta = {
                'text': s,
                'doc_id': doc_idx + 1,
                'sent_id': sent_idx + 1,
                'calc_text': processed
            }
            all_data.append(meta)
            calc_texts.append(processed)

print(f" Preprocessing Selesai.")
print(f" Total Kalimat Valid: {len(all_data)} kalimat")

print("\n Sample Data (Original vs Calculation Input):")
df_prep = pd.DataFrame(all_data)[['text', 'calc_text']]
df_prep.columns = ['Original Text (Display)', 'Cleaned text for Embedding Input (SBERT)']
display(df_prep)
#Embedding Generation (Sentence-BERT)
import pandas as pd
import numpy as np

sent_vecs = embedder.get_embeddings(calc_texts)

query_vec = np.mean(sent_vecs, axis=0)


print(" INFORMASI STRUKTUR DATA:")
print(f"   • Tipe Data Output : {type(sent_vecs)}")
print(f"   • Matriks Kalimat  : {sent_vecs.shape}  -> (Total Kalimat, Dimensi Model)")
print(f"   • Vektor Query     : {query_vec.shape}     -> (Dimensi Model,)")
# (dimensi Sample 5 Kalimat Pertama)

num_preview_dims = 384
cols = [f"Dim_{i+1}" for i in range(num_preview_dims)]

if sent_vecs.ndim == 1:
    df_vec_preview = pd.DataFrame(sent_vecs[:num_preview_dims].reshape(1, -1), columns=cols)
    df_vec_preview.insert(0, "Text Snippet", [calc_text[:10000] ])
elif sent_vecs.ndim == 2:
    df_vec_preview = pd.DataFrame(sent_vecs[:100, :num_preview_dims], columns=cols)
    df_vec_preview.insert(0, "Text Snippet", [t[:1000] for t in calc_texts[:100]])
else:
    raise ValueError("sent_vecs has unexpected dimensions.")

display(df_vec_preview)
# Query Vector
print("\n PREVIEW QUERY VECTOR (CENTROID) (10 Dimensi Awal):")
print("   (Rata-rata dari seluruh vektor di atas, merepresentasikan 'topik inti')")
df_query = pd.DataFrame(query_vec.reshape(1, -1)[:, :500], columns=[f"Dim_{i+1}" for i in range(384)])
display(df_query)

# Nilai
print("\n STATISTIK NILAI VEKTOR:")
print(f"   • Nilai Min dalam Matrix : {np.min(sent_vecs):.4f}")
print(f"   • Nilai Max dalam Matrix : {np.max(sent_vecs):.4f}")
print(f"   • Nilai Mean (Rata-rata) : {np.mean(sent_vecs):.4f}")
# MMR Selection Process (Ranking)

# COMPRESSION_RATE = 0.20
# COMPRESSION_RATE = 0.30
# COMPRESSION_RATE = 0.40
COMPRESSION_RATE = 0.50
# n_teratas= 8

total_sentences_input = len(all_data)
jumlah_terkompresi = int(total_sentences_input * COMPRESSION_RATE)

# selected_data, logs = mmr.select_with_logs(all_data, sent_vecs, query_vec, n=jumlah_terkompresi)
selected_data, logs, heuristic_logs = mmr.select_with_logs(all_data, sent_vecs, query_vec, n=jumlah_terkompresi)

print(f"✅ Jumlah Kalimat Terpilih: {len(selected_data)} dari total {total_sentences_input} kalimat.\n")

print("\n" + "="*80)
df_heuristics = pd.DataFrame(heuristic_logs)
display(df_heuristics)

print("\n" + "="*80)
print("\n TABEL DETAIL SCORING MMR :")
df_logs = pd.DataFrame(logs)

#Output
# df_logs = df_logs[['Step', 'Source', 'MMR Score', 'Relevance', 'Diversity', 'Text']]
df_logs = pd.DataFrame(logs)
display(df_logs)

final_text_parts = []

for item in selected_data:
    final_text_parts.append(item['text'])

extractive_clean = " ".join(final_text_parts)

print("\n Hasil Ekstraktif:")
print("-" * 75)
print(extractive_clean)
print("-" * 75)

inp_model = " ".join(extractive_clean.split()[:512])
print(f"\n Input ke Model Abstractive Siap.")
print(f"   Jumlah Kata: {len(inp_model.split())}")
!pip install rouge_score





import pandas as pd
from rouge_score import rouge_scorer


ground_truth_text_1 = """
Di tengah perlombaan global mengadopsi kecerdasan buatan (AI), talenta Indonesia mulai mengambil peran krusial di pusat inovasi dunia. Product Manager di Google Amerika Serikat, Juan Anugraha Djuwadi, kini menjadi salah satu aktor strategis yang mengarahkan bagaimana teknologi AI dikembangkan agar tetap manusiawi dan berdampak luas bagi pengguna global. Dalam webinar bertajuk “AI Streamline Your Business: Build Internal Apps with AI” baru-baru ini, Juan membedah peta jalan pengembangan AI yang melampaui sekadar kecanggihan teknis. Baginya, kunci utama efektivitas AI terletak pada kegunaannya dalam menjawab persoalan nyata di masyarakat. Juan, yang merupakan alumnus Columbia University, menegaskan bahwa pengguna akhir seringkali tidak mempedulikan kerumitan algoritma di balik sebuah aplikasi. “Pengguna tidak peduli seberapa canggih teknologi di belakang layar. Mereka peduli apakah solusi itu berguna dan menyelesaikan masalah nyata,” ujar Juan, dikutip Kamis (15/1/2026). Prinsip ini diterjemahkan ke dalam dua filosofi kunci: “less is more” dan “the details matter.” Menurutnya, dalam skala pengguna miliaran seperti di Google, detail sekecil apa pun menjadi isu strategis. Kegagalan sistem sebesar satu persen saja dapat berdampak pada jutaan orang. Persfektif ini dinilai sangat relevan bagi pemerintah Indonesia dan perusahaan BUMN yang tengah mengintegrasikan AI dalam layanan publik berskala nasional. Terkait proses pengambilan keputusan, Juan menawarkan pendekatan moderat antara data dan intuisi. Ia mengibaratkan data sebagai kompas untuk optimasi efisiensi dan akurasi, namun terobosan besar tetap membutuhkan visi manusia. “Data memvalidasi masa kini, namun intuisi mendefinisikan masa depan,” ungkapnya. Pendekatan ini menjadi krusial bagi para regulator dan pemimpin perusahaan di Asia Pasifik (APAC) agar tidak hanya bersikap reaktif terhadap tren, tetapi mampu menjadi visioner dalam merancang ekosistem digital. Menyoroti lanskap digital di Tanah Air, Juan melihat adanya perbedaan fase kematangan antara pasar Amerika Serikat (AS) dan Indonesia. Jika AS sudah mapan dalam hal monetisasi perangkat lunak, Indonesia masih berada dalam tahap transisi yang dinamis. Ia memprediksi, seiring berkembangnya ekosistem digital di Indonesia, isu mengenai privasi data, etika AI, dan akuntabilitas akan menjadi agenda utama yang tak terelakkan. Inovasi AI yang sukses di wilayah dengan keberagaman sosial tinggi seperti Indonesia dan APAC haruslah bersifat kontekstual dan berbasis pada kepercayaan. Mantan profesional di Niantic dan Activision ini juga memproyeksikan pergeseran fundamental dalam lima tahun mendatang melalui demokratisasi AI. Ia memperkirakan lahirnya era “software on-the-fly”, di mana perangkat lunak dihasilkan secara real-time sesuai kebutuhan instan pengguna, baik melalui antarmuka teks maupun suara. Ia membuktikan bahwa peran talenta Indonesia bukan sekadar pelengkap, melainkan kontributor strategis yang turut menentukan arah teknologi masa depan yang beretika dan berorientasi pada kepentingan manusia.
""".strip()

ground_truth_text_2 = """
""".strip()

if 'selected_data' in globals() and selected_data:
    system_summary_text = " ".join([item['text'] for item in selected_data])
else:
    print("WARNING: Variable 'selected_data' kosong/tidak ditemukan.")

if system_summary_text and ground_truth_text_1:
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    scores = scorer.score(ground_truth_text_1, system_summary_text)

    print("\n" + "="*60)
    print("HASIL EVALUASI AKHIR (ROUGE SCORE)")
    print(f"Lambda = {mmr.lambda_param}")
    print("="*60)

    print(f"\n SYSTEM SUMMARY (MMR):\n{system_summary_text}")
    print("-" * 60)
    print(f" GROUND TRUTH (Dari Annotator):\n{ground_truth_text_1}")
    print("-" * 60)

    results_data = {
        "Metric": ["ROUGE-1 (Kata)", "ROUGE-2 (Frasa)", "ROUGE-L (Urutan)"],
        "Precision": [scores['rouge1'].precision, scores['rouge2'].precision, scores['rougeL'].precision],
        "Recall": [scores['rouge1'].recall, scores['rouge2'].recall, scores['rougeL'].recall],
        "F1-Score": [scores['rouge1'].fmeasure, scores['rouge2'].fmeasure, scores['rougeL'].fmeasure]
    }

    df_results = pd.DataFrame(results_data)

    print("\nTABEL SKOR:")
    display(df_results.style.format("{:.4f}", subset=["Precision", "Recall", "F1-Score"]))

    f1_r1 = scores['rouge1'].fmeasure
    f1_r2 = scores['rouge2'].fmeasure
    f1_rl = scores['rougeL'].fmeasure
else:
    print(" Evaluasi dibatalkan karena data kosong.")