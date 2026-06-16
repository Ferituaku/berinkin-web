import re
import numpy as np
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
import nltk
import uuid

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextPreprocessor:
    def __init__(self):
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()

    def clean_text_display(self, text: str) -> str:
        remove = [r'^liputan6\.com\s*(?:-|:)\s*',r'^(?:liputan6\.com|com)\s*,\s*[a-z\s]+\s*(?:-|:)\s*',r'BACA JUGA:.*?(?=\n|$)', r'Disclaimer:.*?(?=\n|$)', r'^\s*ADVERTISEMENT.*?(?=\n|$)',
                  r'Perbesar', r'Selengkapnya', r'\d+\s+dari\s+\d+\s+halaman', r'\s*\([A-Za-z0-9/\.\s-]+\)\.?\s*$']
        for p in remove: 
            text = re.sub(p, ' ', text, flags=re.IGNORECASE|re.DOTALL)

        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', text)
        text = re.sub(r'([.,!?])(?=[a-zA-Z])', r'\1 ', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
        text = text.encode('ascii', 'ignore').decode('ascii')

        # Clean currency spacing issues (e.g. Rp 9. 807 -> Rp 9.807)
        while True:
            new_text = re.sub(r'(Rp\s*\d+(?:\.\d+)*)\.\s+(\d+)', r'\1.\2', text, flags=re.IGNORECASE)
            if new_text == text:
                break
            text = new_text

        return re.sub(r'\s+', ' ', text).strip()

    def case_folding_and_remove_artifacts(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'[^a-z\s]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def split_sentences(self, text: str) -> list:
        try: return sent_tokenize(text)
        except: return re.split(r'(?<=[.!?])\s+', text)


class SentenceBERTEmbedder:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, sentences: list):
        if not sentences: return np.array([])
        embeddings = self.model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
        return embeddings


class MMRSelector:
    def __init__(self, lambda_param=0.7):
        self.lambda_param = lambda_param

    def _cosine_similarity(self, A, B):
        dot_product = np.dot(A, B.T)
        norm_a = np.linalg.norm(A, axis=1, keepdims=True)
        norm_b = np.linalg.norm(B, axis=1, keepdims=True)
        denominator = np.dot(norm_a, norm_b.T) + 1e-10
        return dot_product / denominator

    def select(self, sentences_data, embs, query, n=5):
        if not sentences_data: return []

        embs = np.array(embs)
        query = np.array(query)
        if query.ndim == 1: query = query.reshape(1, -1)
        if embs.ndim == 1: embs = embs.reshape(1, -1)

        # Pure cosine similarity relevance score from SBERT (no heuristics, per research notebook)
        sim_to_query = self._cosine_similarity(embs, query).flatten()

        sel_idx = []
        rem_idx = list(range(len(sentences_data)))

        while len(sel_idx) < n and rem_idx:
            step_candidates = []
            selected_vecs = embs[sel_idx] if sel_idx else None
            for i in rem_idx:
                rel = sim_to_query[i]
                div = 0.0
                if selected_vecs is not None:
                    curr_vec = embs[i].reshape(1, -1)
                    sim_to_selected = self._cosine_similarity(curr_vec, selected_vecs)
                    div = np.max(sim_to_selected)
                score = self.lambda_param * rel - (1 - self.lambda_param) * div
                step_candidates.append({"idx": i, "score": score})
            
            best = max(step_candidates, key=lambda x: x['score'])
            sel_idx.append(best['idx'])
            rem_idx.remove(best['idx'])

        return [sentences_data[i] for i in sel_idx]


def summarize_pipeline_generator(articles, compression_rate=0.3, lambda_param=0.7):
    """
    Generator pipeline for clustering and MMR summarization.
    """
    if not articles:
        yield {"progress": 100, "message": "Tidak ada data.", "clusters": []}
        return
        
    yield {"progress": 40, "message": "Membersihkan & memproses teks (Preprocessing)..."}
    preprocessor = TextPreprocessor()
    vectorizer = TfidfVectorizer(max_features=1000)
    
    feats = []
    for d in articles:
        f_text = f"{d['title']} {d['title']} {d.get('content','')[:500]}"
        feats.append(f_text)
    
    vecs = vectorizer.fit_transform(feats).toarray()
    
    yield {"progress": 50, "message": "Membangun klaster topik (Agglomerative Clustering)..."}
    clusterer = AgglomerativeClustering(
        n_clusters=None,
        metric='cosine',
        linkage='average',
        distance_threshold=0.85
    )
    labels = clusterer.fit_predict(vecs)
    
    clusters_dict = {}
    for i, lbl in enumerate(labels):
        if lbl not in clusters_dict: clusters_dict[lbl] = []
        clusters_dict[lbl].append(articles[i])
        
    yield {"progress": 60, "message": "Memuat model Sentence-BERT..."}
    embedder = SentenceBERTEmbedder()
    mmr = MMRSelector(lambda_param=lambda_param)
    
    results = []
    valid_clusters = [lbl for lbl, docs in clusters_dict.items() if len(docs) >= 1]
    total_clusters = len(valid_clusters)
    
    if total_clusters == 0:
        yield {"progress": 100, "message": "Tidak cukup data untuk membentuk klaster.", "clusters": []}
        return

    cluster_idx = 0
    for lbl in valid_clusters:
        docs = clusters_dict[lbl]
        cluster_idx += 1
        
        yield {"progress": 60 + int(35 * (cluster_idx/total_clusters)), "message": f"Mengekstraksi vektor & Seleksi MMR (Klaster {cluster_idx}/{total_clusters})..."}
        
        all_data = []
        calc_texts = []
        
        for doc_idx, art in enumerate(docs):
            clean = preprocessor.clean_text_display(art['content'])
            sents = preprocessor.split_sentences(clean)
            for sent_idx, s in enumerate(sents):
                s = s.strip()
                if len(s) >= 20 and re.search(r'[a-zA-Z]', s):
                    processed = preprocessor.case_folding_and_remove_artifacts(s)
                    all_data.append({
                        'text': s,
                        'doc_id': doc_idx + 1,
                        'sent_id': sent_idx + 1,
                        'calc_text': processed
                    })
                    calc_texts.append(processed)
        
        if not calc_texts: continue
        
        sent_vecs = embedder.get_embeddings(calc_texts)
        query_vec = np.mean(sent_vecs, axis=0)
        
        # Calculate compression based on total sentences in the cluster (original pipeline)
        rate = compression_rate / 100.0 if compression_rate > 1.0 else compression_rate
        total_sentences_input = len(all_data)
        jumlah_terkompresi = max(2, int(total_sentences_input * rate))
        
        selected_data = mmr.select(all_data, sent_vecs, query_vec, n=jumlah_terkompresi)
        
        # Sort back to chronological/original order for better readability
        selected_data.sort(key=lambda x: (x['doc_id'], x['sent_id']))
        summary_text = " ".join([item['text'] for item in selected_data])
        
        results.append({
            "cluster_id": str(uuid.uuid4()),
            "topic_title": docs[0]['title'],
            "article_count": len(docs),
            "summary": summary_text,
            "articles": docs
        })
        
    yield {"progress": 100, "message": "Konvergensi selesai.", "clusters": results}
