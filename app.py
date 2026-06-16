import streamlit as st
import sys
import os
import re
import uuid
import datetime
import json
import base64
import numpy as np

# Add backend directory to sys.path to allow imports from backend
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# --- SBERT Model Cache Optimization ---
from sentence_transformers import SentenceTransformer
from core.summarizer import SentenceBERTEmbedder

@st.cache_resource
def get_cached_sbert_model():
    """Cache the SentenceTransformer model to prevent reloading on every run."""
    return SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Patch the init of SentenceBERTEmbedder to use the cached model instance
def patched_init(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
    self.model = get_cached_sbert_model()

SentenceBERTEmbedder.__init__ = patched_init

# --- Database & Pipeline Imports ---
from database import init_db, SummaryHistory, SessionLocal
from core.scraper import scrape_articles_pipeline_generator
from core.summarizer import summarize_pipeline_generator

# Initialize DB on startup
try:
    init_db()
except Exception as e:
    st.warning(f"Could not initialize database: {e}")

# Download NLTK data needed for sentence tokenization (runs once, cached by Streamlit Cloud)
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception:
    pass

import html as _html  # for escaping user-generated text safely in HTML templates

# --- Helper Functions ---
def get_base64_image(image_path):
    """Encodes a local image to base64 for embedding in HTML."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    return ""

def _render_card_grid(clusters, mode, card_type="multi"):
    """Render cluster cards as a CSS-grid iframe (bypasses Streamlit HTML sanitizer).

    Uses st.components.v1.html() so the HTML is rendered inside an iframe with
    no Streamlit markdown post-processing. Anchor tags use target='_parent' so
    clicking a card navigates the parent Streamlit page.
    """
    import html as _h
    cards = []
    for idx, cluster in enumerate(clusters):
        cluster_key = cluster.get('cluster_id', str(idx))
        title     = _h.escape(str(cluster.get('topic_title', '')))
        summary   = _h.escape(str(cluster.get('summary', ''))[:280])
        category  = _h.escape(str(cluster.get('category', '')))
        art_count = cluster.get('article_count', 1)
        comp      = cluster.get('compression_rate', 30)
        lmb       = cluster.get('lambda_value', 0.7)

        if card_type == "multi":
            label        = f"KLASTER #{idx + 1}"
            border_col   = "#064e3b"
            title_col    = "#003527"
            action_txt   = "Baca Ringkasan"
            action_col   = "#064e3b"
            opacity      = "1"
            corner_nodes = """
                <div class="cn tl"></div><div class="cn tr"></div>
                <div class="cn bl"></div><div class="cn br"></div>"""
            badges_extra = (
                f'<span class="badge-cat">{category}</span>' if category else ''
            )
            badges = (
                f'<span class="badge">Kompresi: {comp}%</span>'
                f'<span class="badge">Lambda: {lmb}</span>'
                f'{badges_extra}'
            )
        else:
            label        = f"BERITA #{idx + 1}"
            border_col   = "#bfc9c3"
            title_col    = "#1a1c1a"
            action_txt   = "Lihat Detail"
            action_col   = "#707974"
            opacity      = "0.8"
            corner_nodes = ""
            badges       = '<span class="badge-warn">Tidak Teringkas</span>'

        cards.append(f"""
<a class="card" href="?page=detail&id={cluster_key}&mode={mode}"
   target="_parent" style="opacity:{opacity};">
  {corner_nodes}
  <div class="card-header" style="border-left-color:{border_col};">
    <span class="label">{label}</span>
    <span class="src"><span class="mi">article</span>{art_count} SUMBER</span>
  </div>
  <div class="card-body">
    <h3 style="color:{title_col};">{title}</h3>
    <div class="badges">{badges}</div>
    <p class="excerpt">{summary}</p>
  </div>
  <div class="card-foot" style="color:{action_col};">
    <span>{action_txt}</span>
    <span class="mi">arrow_forward</span>
  </div>
</a>""")

    rows = max(1, (len(clusters) + 2) // 3)
    card_h = 320  # px per card row
    iframe_h = rows * card_h + 24

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:'Inter',sans-serif;padding:2px 0;}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}}
.card{{
  background:rgba(255,255,255,0.9);
  border:0.5px solid #bfc9c3;
  padding:24px;
  position:relative;
  display:flex;
  flex-direction:column;
  gap:14px;
  min-height:300px;
  text-decoration:none;
  color:#1a1c1a;
  transition:all 0.25s ease;
  border-radius:0;
}}
.card:hover{{
  border-color:#064e3b;
  background:rgba(255,255,255,1);
  box-shadow:0 8px 24px -4px rgba(0,53,39,0.1);
  transform:translateY(-2px);
}}
.cn{{position:absolute;width:6px;height:6px;background:#064e3b;}}
.tl{{top:-3px;left:-3px}}.tr{{top:-3px;right:-3px}}
.bl{{bottom:-3px;left:-3px}}.br{{bottom:-3px;right:-3px}}
.card-header{{
  display:flex;justify-content:space-between;align-items:center;
  border-left:2px solid;padding-left:10px;
}}
.label{{font-size:10px;font-weight:700;color:#404944;letter-spacing:.1em;text-transform:uppercase;}}
.src{{display:flex;align-items:center;gap:3px;font-size:10px;font-weight:700;color:#707974;letter-spacing:.05em;}}
.mi{{font-family:'Material Symbols Outlined';font-size:15px;font-weight:400;line-height:1;}}
.card-body{{flex:1;display:flex;flex-direction:column;gap:10px;}}
h3{{font-family:'Newsreader',serif;font-size:20px;line-height:1.35;font-weight:500;}}
.badges{{display:flex;gap:6px;flex-wrap:wrap;}}
.badge{{font-size:9px;font-weight:700;background:#e3e2e0;color:#404944;padding:3px 7px;text-transform:uppercase;letter-spacing:.05em;}}
.badge-cat{{font-size:9px;font-weight:700;background:#95d3ba;color:#002117;padding:3px 7px;text-transform:uppercase;}}
.badge-warn{{font-size:9px;font-weight:700;background:#ffdad6;color:#ba1a1a;border:0.5px solid #ffdad6;padding:3px 7px;text-transform:uppercase;}}
.excerpt{{font-size:13px;line-height:1.55;color:#404944;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}}
.card-foot{{
  margin-top:auto;padding-top:14px;border-top:0.5px solid #e3e2e0;
  display:flex;justify-content:space-between;align-items:center;
  font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;
}}
</style>
</head>
<body>
<div class="grid">
{''.join(cards)}
</div>
</body>
</html>"""

    st.components.v1.html(full_html, height=iframe_h, scrolling=False)

def split_summary_into_paragraphs(summary_text, sentences_per_paragraph=3):
    """Splits summary text into paragraphs of N sentences each.
    Uses NLTK punkt tokenizer if available, falls back to simple regex.
    """
    if not summary_text or not summary_text.strip():
        return [summary_text or ""]

    # Try NLTK punkt tokenizer first (most robust for Indonesian)
    try:
        import nltk
        try:
            sentences = nltk.tokenize.sent_tokenize(summary_text, language='indonesian')
        except Exception:
            # Fall back to English tokenizer
            sentences = nltk.tokenize.sent_tokenize(summary_text)
    except Exception:
        # Simple fallback: split on . ! ? followed by space + capital letter
        import re as _re
        raw = _re.split(r'(?<=[.!?])\s+(?=[A-Z"(])', summary_text)
        sentences = [s.strip() for s in raw if s.strip()]

    if not sentences:
        return [summary_text]

    paragraphs = []
    current_paragraph = []
    for idx, sentence in enumerate(sentences):
        stripped = sentence.strip()
        if stripped:
            current_paragraph.append(stripped)
        if len(current_paragraph) >= sentences_per_paragraph:
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    return paragraphs if paragraphs else [summary_text]

# Cache file functions for local cluster results (similar to localStorage in React)
CACHE_FILE = "berinkin_clusters_cache.json"

def save_clusters_to_cache(clusters):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(clusters, f)
    except Exception as e:
        st.error(f"Gagal menyimpan cache lokal: {e}")

def load_clusters_from_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

# --- Page Setup & CSS Injection ---
st.set_page_config(
    page_title="Berinkin - Berita Ringkasan Terkini",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom styling representing "Editorial Minimalism"
def inject_custom_css():
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
        <style>
            /* Reset & Core Styling */
            html, body, [data-testid="stAppViewContainer"] {
                background-color: #faf9f6 !important;
                color: #1a1c1a !important;
                font-family: 'Inter', sans-serif !important;
            }
            [data-testid="stHeader"] {
                display: none !important;
            }
            .block-container {
                padding-top: 0rem !important;
                padding-bottom: 3rem !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }
            
            /* Typography */
            h1, h2, h3, .serif-text {
                font-family: 'Newsreader', serif !important;
                color: #003527 !important;
                font-weight: 600 !important;
            }
            
            /* Hide Streamlit elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Header Navigation styling */
            .header-nav {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 80px;
                background-color: rgba(250, 249, 246, 0.85);
                backdrop-filter: blur(16px);
                border-bottom: 0.5px solid #bfc9c3;
                z-index: 999;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .header-nav-container {
                width: 100%;
                max-width: 1200px;
                padding: 0 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .header-nav .brand {
                font-family: 'Newsreader', serif;
                font-size: 28px;
                font-weight: 700;
                color: #003527 !important;
                text-decoration: none;
                letter-spacing: -0.02em;
            }
            .header-nav .nav-links {
                display: flex;
                gap: 32px;
                align-items: center;
            }
            .header-nav .nav-link {
                font-family: 'Newsreader', serif;
                font-size: 18px;
                color: #707974;
                text-decoration: none;
                position: relative;
                padding-bottom: 4px;
                transition: color 0.3s;
            }
            .header-nav .nav-link:hover {
                color: #003527;
            }
            .header-nav .nav-link.active {
                color: #003527;
                font-weight: 500;
            }
            .header-nav .nav-link.active::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 2px;
                background-color: #003527;
            }
            
            /* Main Container Padding */
            .main-content {
                margin-top: 100px;
                width: 100%;
                max-width: 1200px;
                margin-left: auto;
                margin-right: auto;
            }
            
            /* Button styles */
            .premium-button {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background-color: #064e3b;
                color: #ffffff !important;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                padding: 16px 32px;
                border-radius: 9999px;
                border: 0.5px solid #95d3ba;
                text-decoration: none;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .premium-button:hover {
                background-color: #003527;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15);
                transform: translateY(-1px);
            }
            
            /* Cluster Cards Grid */
            .cluster-card {
                background-color: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(12px);
                border: 0.5px solid #bfc9c3;
                padding: 32px;
                position: relative;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                gap: 20px;
                height: 100%;
                text-decoration: none;
                color: inherit !important;
            }
            .cluster-card:hover {
                border-color: #064e3b;
                background-color: rgba(255, 255, 255, 0.98);
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
            }
            .cluster-card .corner-node {
                position: absolute;
                width: 6px;
                height: 6px;
                background-color: #064e3b;
            }
            .cluster-card .top-left { top: -3px; left: -3px; }
            .cluster-card .top-right { top: -3px; right: -3px; }
            .cluster-card .bottom-left { bottom: -3px; left: -3px; }
            .cluster-card .bottom-right { bottom: -3px; right: -3px; }
            
            /* Leaf Canvas Iframe Hack */
            iframe[title="streamlit_app.render_falling_leaves"] {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: -2 !important;
                pointer-events: none !important;
                border: none !important;
            }
            
            /* Form container styling */
            .form-container {
                background-color: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(12px);
                border: 0.5px solid #bfc9c3;
                padding: 40px;
                position: relative;
            }
            .form-container::before {
                content: '';
                position: absolute;
                top: -3px; left: -3px; width: 6px; height: 6px; background-color: #064e3b;
            }
            .form-container::after {
                content: '';
                position: absolute;
                top: -3px; right: -3px; width: 6px; height: 6px; background-color: #064e3b;
            }
            .form-bottom-left {
                position: absolute;
                bottom: -3px; left: -3px; width: 6px; height: 6px; background-color: #064e3b;
            }
            .form-bottom-right {
                position: absolute;
                bottom: -3px; right: -3px; width: 6px; height: 6px; background-color: #064e3b;
            }
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar {
                width: 6px;
            }
            ::-webkit-scrollbar-track {
                background: #faf9f6;
            }
            ::-webkit-scrollbar-thumb {
                background: #bfc9c3;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

inject_custom_css()

# --- Falling Leaves Overlay ---
def render_falling_leaves():
    leaves_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
        margin: 0;
        padding: 0;
        overflow: hidden;
        background: transparent;
    }
    canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
    }
    </style>
    </head>
    <body>
    <canvas id="leafCanvas"></canvas>
    <script>
    const canvas = document.getElementById('leafCanvas');
    const ctx = canvas.getContext('2d');
    
    let leaves = [];
    const numLeaves = Math.min(Math.floor(window.innerWidth / 35), 40);
    const colors = [
      'rgba(6, 78, 59, 0.15)',   // primary-container
      'rgba(149, 211, 186, 0.25)', // primary-fixed-dim
      'rgba(191, 201, 195, 0.18)', // outline-variant
      'rgba(43, 105, 84, 0.12)'    // surface-tint
    ];
    
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();
    
    function createLeaf(resetY = false) {
        return {
            x: Math.random() * canvas.width,
            y: resetY ? -20 : Math.random() * canvas.height,
            size: Math.random() * 5 + 4, // 4 to 9
            speedX: Math.random() * 0.6 - 0.3,
            speedY: Math.random() * 0.5 + 0.3, // 0.3 to 0.8
            rotation: Math.random() * Math.PI * 2,
            rotationSpeed: (Math.random() - 0.5) * 0.02,
            oscillationSpeed: Math.random() * 0.008 + 0.004,
            oscillationPhase: Math.random() * Math.PI * 2,
            color: colors[Math.floor(Math.random() * colors.length)]
        };
    }
    
    for (let i = 0; i < numLeaves; i++) {
        leaves.push(createLeaf());
    }
    
    function drawLeaf(leaf) {
        ctx.save();
        ctx.translate(leaf.x, leaf.y);
        ctx.rotate(leaf.rotation);
        
        ctx.beginPath();
        ctx.moveTo(0, -leaf.size);
        ctx.bezierCurveTo(leaf.size * 0.8, -leaf.size * 0.5, leaf.size * 0.8, leaf.size * 0.8, 0, leaf.size);
        ctx.bezierCurveTo(-leaf.size * 0.8, leaf.size * 0.8, -leaf.size * 0.8, -leaf.size * 0.5, 0, -leaf.size);
        ctx.fillStyle = leaf.color;
        ctx.fill();
        
        // stem vein
        ctx.beginPath();
        ctx.moveTo(0, -leaf.size * 0.8);
        ctx.lineTo(0, leaf.size * 1.1);
        ctx.strokeStyle = 'rgba(0,0,0,0.1)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
        
        ctx.restore();
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        leaves.forEach((leaf) => {
            leaf.x += Math.sin(leaf.oscillationPhase) * 0.3 + leaf.speedX;
            leaf.y += leaf.speedY;
            leaf.rotation += leaf.rotationSpeed;
            leaf.oscillationPhase += leaf.oscillationSpeed;
            
            if (leaf.y > canvas.height + 20 || leaf.x < -20 || leaf.x > canvas.width + 20) {
                Object.assign(leaf, createLeaf(true));
            }
            
            drawLeaf(leaf);
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    </script>
    </body>
    </html>
    """
    st.components.v1.html(leaves_html, height=1, scrolling=False)

render_falling_leaves()

# --- Page Routing System ---
# Get current URL query parameter
query_params = st.query_params
current_page = query_params.get("page", "home")

# Render Top Navigation Bar HTML
active_home = "active" if current_page == "home" else ""
active_peringkas = "active" if current_page == "peringkas" else ""
active_hasil = "active" if current_page in ["hasil", "detail"] else ""

st.markdown(
    f"""
    <div class="header-nav">
        <div class="header-nav-container">
            <a href="?page=home" target="_self" class="brand">Berin'kin</a>
            <div class="nav-links">
                <a href="?page=home" target="_self" class="nav-link {active_home}">Beranda</a>
                <a href="?page=peringkas" target="_self" class="nav-link {active_peringkas}">Peringkas</a>
                <a href="?page=hasil" target="_self" class="nav-link {active_hasil}">Hasil</a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Render main page content wrapper
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ----------------- 1. BERANDA (HOME) PAGE -----------------
if current_page == "home":
    banyan_base64 = get_base64_image("frontend/public/banyan.png")
    
    # Hero Section
    st.markdown(
        f"""
        <div style="text-align: center; max-width: 1200px; margin: 40px auto 100px auto; padding: 0 40px;">
            <div style="margin-bottom: 32px; position: relative; width: 96px; height: 96px; margin-left: auto; margin-right: auto;">
                <img src="{banyan_base64}" alt="Berinkin Logo" style="width: 100%; height: 100%; object-fit: contain; opacity: 0.9;" />
            </div>
            <h1 style="font-size: 56px; line-height: 1.1; margin-bottom: 24px; font-weight: 600; font-family: 'Newsreader', serif;">
                Berin'kin
            </h1>
            <p style="font-size: 18px; line-height: 1.6; color: #404944; max-width: 650px; margin-left: auto; margin-right: auto; margin-bottom: 48px; font-weight: 300;">
                Merangkum kekacauan data yang terfragmentasi menjadi satu ringkasan pengetahuan yang berwibawa.
            </p>
            <div style="position: relative; display: inline-block;">
                <a href="?page=peringkas" target="_self" class="premium-button">
                    <span>MULAI PERINGKASAN</span>
                    <span class="material-symbols-outlined" style="font-size: 16px;">arrow_forward</span>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Philosophy Section
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="width: 32px; height: 0.5px; background-color: #003527;"></div>
                <span style="font-size: 12px; font-weight: 600; color: #003527; letter-spacing: 0.1em; text-transform: uppercase;">Filosofi</span>
            </div>
            <h2 style="font-size: 36px; line-height: 1.2; font-weight: 500; margin-bottom: 24px; font-family: 'Newsreader', serif;">
                Metafora Pohon Beringin
            </h2>
            <p style="font-size: 16px; line-height: 1.6; color: #404944; margin-bottom: 24px; font-weight: 400;">
                Di era kelebihan informasi, kejelasan adalah sebuah kemewahan. Sistem Berinkin terinspirasi oleh pohon Beringin—jaringan akar dan cabang yang kompleks yang pada akhirnya menyatu menjadi satu batang yang tak tergoyahkan.
            </p>
            <p style="font-size: 16px; line-height: 1.6; color: #404944; font-weight: 400;">
                Kami tidak sekadar mengumpulkan; kami merangkum. Dengan secara sistematis mengumpulkan narasi yang terfragmentasi di lanskap digital, kami menyintesisnya menjadi ringkasan yang padu dan berketepatan tinggi yang menghargai waktu dan kecerdasan Anda.
            </p>
            """,
            unsafe_allow_html=True
        )
    with col2:
        # Styled video container
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        if os.path.exists("frontend/public/tree-video.mp4"):
            st.video("frontend/public/tree-video.mp4", autoplay=True, loop=True, muted=True)
        else:
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: center; height: 300px; color: #707974; font-style: italic; border: 0.5px solid #bfc9c3;">
                    Tree Video Asset Not Found
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # Technical Pipeline Flowchart Section
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 64px;">
            <h2 style="font-size: 36px; line-height: 1.2; font-weight: 500; margin-bottom: 16px; font-family: 'Newsreader', serif;">Alur Peringkasan</h2>
            <p style="font-size: 16px; color: #404944; font-weight: 400;">Sebuah metodologi empat langkah yang ketat untuk peringkasan informasi.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render flowchart HTML
    pipeline_html = """
    <div class="pipeline-container">
        <div class="pipeline-line"></div>
        
        <div class="pipeline-step">
            <div class="pipeline-node"></div>
            <div class="pipeline-content left">
                <div class="step-num">FASE 01</div>
                <div class="step-title">Pengambilan Berita</div>
                <div class="step-desc">Ekstraksi sistematis data mentah dan terfragmentasi dari portal resmi di seluruh jaringan.</div>
            </div>
            <div class="pipeline-icon right">
                <span class="material-symbols-outlined icon-display">travel_explore</span>
            </div>
        </div>
        
        <div class="pipeline-step reverse">
            <div class="pipeline-node"></div>
            <div class="pipeline-content right">
                <div class="step-num">FASE 02</div>
                <div class="step-title">Pengelompokan Topik</div>
                <div class="step-desc">Pengelompokan algoritmik dari kesamaan semantik, memastikan beragam perspektif disejajarkan ke dalam topik-topik terpisah.</div>
            </div>
            <div class="pipeline-icon left">
                <span class="material-symbols-outlined icon-display">hub</span>
            </div>
        </div>
        
        <div class="pipeline-step">
            <div class="pipeline-node"></div>
            <div class="pipeline-content left">
                <div class="step-num">FASE 03</div>
                <div class="step-title">Peringkasan BERT &amp; MMR</div>
                <div class="step-desc">Penyematan semantik mendalam dipadukan dengan Maximal Marginal Relevance untuk mengekstrak informasi yang paling menonjol dan tidak berlebihan.</div>
            </div>
            <div class="pipeline-icon right">
                <span class="material-symbols-outlined icon-display">compress</span>
            </div>
        </div>
        
        <div class="pipeline-step reverse">
            <div class="pipeline-node"></div>
            <div class="pipeline-content right">
                <div class="step-num">FASE 04</div>
                <div class="step-title">Hasil Ringkasan</div>
                <div class="step-desc">Keluaran akhir: batang narasi otoritatif yang dirangkum tanpa kebisingan dan pengulangan.</div>
            </div>
            <div class="pipeline-icon left">
                <span class="material-symbols-outlined icon-display">task_alt</span>
            </div>
        </div>
    </div>
    """
    st.markdown(pipeline_html, unsafe_allow_html=True)
    
    # Footer
    st.markdown("<br><br><br><hr style='border-color: #bfc9c3;'><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; font-size: 12px; color: #707974; font-family: 'Inter', sans-serif;">
            <div>© 2026 Berin'kin. Berita Ringkas Terkini.</div>
            <div style="display: flex; align-items: center; gap: 6px; padding: 6px 12px; border: 0.5px solid rgba(191, 201, 195, 0.5); background-color: #f4f3f1; border-radius: 999px;">
                <span>Crafted with</span>
                <span class="material-symbols-outlined" style="font-size: 14px; color: #064e3b; font-variation-settings: 'FILL' 1;">psychiatry</span>
                <span>by <span style="font-weight: 500; color: #003527;">Ferro Putra</span></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- 2. PERINGKAS (CONFIG) PAGE -----------------
elif current_page == "peringkas":
    st.markdown(
        """
        <div style="text-align: center; max-width: 650px; margin: 0 auto 64px auto;">
            <h1 style="font-size: 48px; line-height: 1.1; color: #003527; margin-bottom: 16px; font-family: 'Newsreader', serif; font-weight: 600;">Ringkasan Pikiran</h1>
            <p style="font-size: 18px; color: #404944; font-weight: 300; line-height: 1.6;">Konfigurasikan parameter ekstraksi untuk mensintesis berita hari ini secara mendalam.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # We build the container for the form
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-bottom-left"></div><div class="form-bottom-right"></div>', unsafe_allow_html=True)
    
    # Form fields using native Streamlit widgets styled with custom classes
    categories = {
        "tekno": "Teknologi & Inovasi",
        "crypto": "Kripto & Blockchain",
        "bola": "Sepak Bola & Olahraga",
        "otomotif": "Otomotif & Kendaraan",
        "health": "Kesehatan & Gaya Hidup",
        "saham": "Pasar Saham",
        "bisnis": "Bisnis & Ekonomi"
    }
    
    col_a, col_b = st.columns(2)
    with col_a:
        category_label = st.selectbox(
            "KATEGORI BERITA",
            options=list(categories.values()),
            index=0
        )
        # Reverse map category label to key
        category_key = [k for k, v in categories.items() if v == category_label][0]
        
    with col_b:
        target_date = st.date_input(
            "TANGGAL BERITA",
            value=datetime.date.today()
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    max_articles = st.slider(
        "TARGET JUMLAH BERITA (ARTIKEL)",
        min_value=5,
        max_value=50,
        value=15,
        step=5
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Advanced Options Accordion
    with st.expander("OPSI LANJUTAN", expanded=False):
        st.markdown(
            """
            <div style="font-size: 14px; color: #404944; font-style: italic; border-left: 2px solid #e9c349; padding-left: 12px; margin-bottom: 24px; line-height: 1.5;">
                Nilai optimal berbasis riset untuk peringkasan multi-dokumen ekstraktif telah dikonfigurasi sebelumnya. Menyesuaikan nilai ini memerlukan pemahaman tentang algoritma MMR (Maximal Marginal Relevance).
            </div>
            """,
            unsafe_allow_html=True
        )
        compression = st.slider(
            "TINGKAT KOMPRESI (%)",
            min_value=20,
            max_value=50,
            value=30,
            step=5,
            help="20% menghasilkan ringkasan yang padat (sedikit kalimat). 50% menghasilkan ringkasan yang lebih lengkap."
        )
        lambda_param = st.slider(
            "LAMBDA MMR",
            min_value=0.1,
            max_value=0.9,
            value=0.7,
            step=0.1,
            help="0.1 mengutamakan keberagaman informasi (mengurangi redundansi). 0.9 mengutamakan kesesuaian semantik dengan topik utama."
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Trigger button centered
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        start_btn = st.button("MULAI MERINGKAS", use_container_width=True, type="primary")
        
    if start_btn:
        # Start Pipeline Loading Overlay
        progress_placeholder = st.empty()
        
        # Helper logs formatting
        date_str = target_date.strftime("%Y-%m-%d")
        
        try:
            articles = []
            
            # Step 1: Scrape
            scraper_gen = scrape_articles_pipeline_generator(category_key, date_str, max_articles)
            for update in scraper_gen:
                prog = update.get("progress", 0)
                msg = update.get("message", "Scraping...")
                
                # Check for results
                if "results" in update:
                    articles = update.pop("results")
                    
                progress_placeholder.markdown(f"""
                <div class="loading-overlay">
                    <div class="loading-container">
                        <div class="spinning-icon">all_inclusive</div>
                        <h1 class="loading-title">Menenun Ringkasan...</h1>
                        <div class="loading-percentage">{prog}<span style="font-size: 20px; opacity: 0.6; margin-left: 4px;">%</span></div>
                        <div class="loading-message">{msg}</div>
                        <div class="loading-progress-line" style="width: {prog}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            if not articles:
                progress_placeholder.markdown(f"""
                <div class="loading-overlay">
                    <div class="loading-container">
                        <h1 class="loading-title" style="color:#ba1a1a;">Tidak Ada Artikel</h1>
                        <p style="font-size: 16px; color: #404944; margin-bottom: 24px;">Tidak ditemukan berita untuk kategori dan tanggal tersebut.</p>
                        <a href="?page=peringkas" target="_self" class="premium-button" style="background-color:#707974; border-color:#bfc9c3;">KEMBALI</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.stop()
                
            # Step 2: Summarize (Clustering & MMR)
            final_clusters = []
            summarizer_gen = summarize_pipeline_generator(articles, compression_rate=compression, lambda_param=lambda_param)
            
            for update in summarizer_gen:
                prog = update.get("progress", 0)
                msg = update.get("message", "Clustering & Summarizing...")
                
                if "clusters" in update:
                    final_clusters = update.pop("clusters")
                    
                progress_placeholder.markdown(f"""
                <div class="loading-overlay">
                    <div class="loading-container">
                        <div class="spinning-icon">all_inclusive</div>
                        <h1 class="loading-title">Menenun Ringkasan...</h1>
                        <div class="loading-percentage">{prog}<span style="font-size: 20px; opacity: 0.6; margin-left: 4px;">%</span></div>
                        <div class="loading-message">{msg}</div>
                        <div class="loading-progress-line" style="width: {prog}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if final_clusters:
                # Add metadata parameters to each cluster
                for c in final_clusters:
                    c['compression_rate'] = compression
                    c['lambda_value'] = lambda_param
                    c['category'] = category_key
                    c['date'] = date_str
                
                # Save to local cache file
                save_clusters_to_cache(final_clusters)
                
                # Save to MySQL database if SessionLocal is available
                try:
                    db = SessionLocal()
                    if db:
                        for c in final_clusters:
                            history = SummaryHistory(
                                id=str(uuid.uuid4()),
                                date_crawled=target_date,
                                category=category_key,
                                cluster_topic=c['topic_title'],
                                article_count=c['article_count'],
                                summary_text=c['summary'],
                                compression_rate=float(compression) / 100.0,
                                lambda_value=lambda_param
                            )
                            db.add(history)
                        db.commit()
                        db.close()
                except Exception as db_err:
                    print(f"Warning: Failed to save to database: {db_err}")
                
                # Complete loading success and trigger transition
                progress_placeholder.empty()
                st.query_params["page"] = "hasil"
                st.rerun()
            else:
                progress_placeholder.markdown(f"""
                <div class="loading-overlay">
                    <div class="loading-container">
                        <h1 class="loading-title" style="color:#ba1a1a;">Gagal Meringkas</h1>
                        <p style="font-size: 16px; color: #404944; margin-bottom: 24px;">Jumlah data berita tidak mencukupi untuk membentuk klaster.</p>
                        <a href="?page=peringkas" target="_self" class="premium-button" style="background-color:#707974; border-color:#bfc9c3;">KEMBALI</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.stop()
                
        except Exception as err:
            progress_placeholder.markdown(f"""
            <div class="loading-overlay">
                <div class="loading-container">
                    <h1 class="loading-title" style="color:#ba1a1a;">System Error</h1>
                    <p style="font-size: 16px; color: #404944; margin-bottom: 24px;">{err}</p>
                    <a href="?page=peringkas" target="_self" class="premium-button" style="background-color:#707974; border-color:#bfc9c3;">KEMBALI</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.stop()

# ----------------- 3. HASIL (RESULTS LIST) PAGE -----------------
elif current_page == "hasil":
    # Tab selector for Current Run vs Database History
    run_mode = st.radio(
        "Tinjau Hasil Dari:",
        options=["Hasil Ringkasan Terkini", "Riwayat Database"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    clusters = []
    
    if run_mode == "Hasil Ringkasan Terkini":
        clusters = load_clusters_from_cache()
        
        # Header Section
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 0.5px solid #bfc9c3; padding-bottom: 32px; margin-bottom: 48px; flex-wrap: wrap; gap: 24px;">
                <div style="max-width: 700px;">
                    <h1 style="font-size: 48px; line-height: 1.1; color: #064e3b; font-family: 'Newsreader', serif; margin-bottom: 16px;">Hasil Klasterisasi</h1>
                    <p style="font-size: 18px; color: #404944; font-weight: 300; line-height: 1.6;">Tinjauan komprehensif dari berbagai sumber informasi yang dikurasi dan diklasterisasi berdasarkan topik relevan.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if clusters:
            # Clear cache action button
            if st.button("BERSIHKAN HASIL", type="secondary"):
                if os.path.exists(CACHE_FILE):
                    os.remove(CACHE_FILE)
                st.query_params["page"] = "hasil"
                st.rerun()
                
    else:
        # Load from database history
        try:
            db = SessionLocal()
            if db:
                db_histories = db.query(SummaryHistory).order_by(SummaryHistory.created_at.desc()).all()
                for h in db_histories:
                    clusters.append({
                        "cluster_id": h.id,
                        "topic_title": h.cluster_topic,
                        "article_count": h.article_count,
                        "summary": h.summary_text,
                        "compression_rate": int(h.compression_rate * 100) if h.compression_rate <= 1.0 else int(h.compression_rate),
                        "lambda_value": h.lambda_value,
                        "category": h.category,
                        "date": h.date_crawled.strftime("%Y-%m-%d") if h.date_crawled else "",
                        "articles": [] # Articles list is not saved in MySQL DB
                    })
                db.close()
        except Exception as db_err:
            st.error(f"Gagal memuat riwayat database: {db_err}")
            
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 0.5px solid #bfc9c3; padding-bottom: 32px; margin-bottom: 48px; flex-wrap: wrap; gap: 24px;">
                <div style="max-width: 700px;">
                    <h1 style="font-size: 48px; line-height: 1.1; color: #064e3b; font-family: 'Newsreader', serif; margin-bottom: 16px;">Riwayat Ringkasan</h1>
                    <p style="font-size: 18px; color: #404944; font-weight: 300; line-height: 1.6;">Daftar seluruh ringkasan berita yang pernah dibuat dan tersimpan di dalam database MySQL.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    if not clusters:
        st.markdown(
            """
            <div style="text-align: center; padding: 80px 0; border: 0.5px dashed #bfc9c3; background-color: rgba(255,255,255,0.5);">
                <span class="material-symbols-outlined" style="font-size: 64px; color: #bfc9c3; margin-bottom: 16px;">hourglass_empty</span>
                <h2 style="font-size: 24px; font-family: 'Newsreader', serif; color: #1a1c1a; margin-bottom: 8px;">Belum ada hasil klasterisasi</h2>
                <p style="color: #404944; margin-bottom: 24px;">Silakan pergi ke halaman Peringkas untuk mulai merangkum berita hari ini.</p>
                <a href="?page=peringkas" target="_self" class="premium-button">Mulai Meringkas</a>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Split clusters into Multi-Article (Klaster Terpadu) and Single-Article (Berita Tunggal)
        multi_clusters = [c for c in clusters if c.get('article_count', 0) > 1]
        single_clusters = [c for c in clusters if c.get('article_count', 0) <= 1]
        safe_mode = 'db' if run_mode != 'Hasil Ringkasan Terkini' else 'cache'

        # Render Multi-Article Clusters
        if multi_clusters:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                    <h2 style="font-size: 14px; font-weight: 700; color: #404944; letter-spacing: 0.2em; text-transform: uppercase; margin: 0;">Klaster Terpadu</h2>
                    <div style="height: 0.5px; background-color: #bfc9c3; flex-grow: 1;"></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            _render_card_grid(multi_clusters, safe_mode, card_type="multi")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # Render Single-Article Outliers
        if single_clusters:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                    <h2 style="font-size: 14px; font-weight: 700; color: #404944; letter-spacing: 0.2em; text-transform: uppercase; margin: 0;">Berita Tunggal</h2>
                    <div style="height: 0.5px; background-color: #bfc9c3; flex-grow: 1;"></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            _render_card_grid(single_clusters, safe_mode, card_type="single")


# ----------------- 4. DETAIL RINGKASAN TOPiK PAGE -----------------
elif current_page == "detail":
    cluster_id = query_params.get("id")
    mode = query_params.get("mode", "cache")
    
    cluster_data = None
    
    # Load cluster details
    if mode == "cache":
        clusters = load_clusters_from_cache()
        # Find by ID or index
        found = [c for c in clusters if c.get('cluster_id') is not None and str(c.get('cluster_id')) == str(cluster_id)]
        if found:
            cluster_data = found[0]
        else:
            # Fallback to index lookup
            try:
                cluster_data = clusters[int(cluster_id)]
            except:
                pass
    else:
        # Load from MySQL database
        try:
            db = SessionLocal()
            if db:
                h = db.query(SummaryHistory).filter(SummaryHistory.id == cluster_id).first()
                if h:
                    cluster_data = {
                        "cluster_id": h.id,
                        "topic_title": h.cluster_topic,
                        "article_count": h.article_count,
                        "summary": h.summary_text,
                        "compression_rate": int(h.compression_rate * 100) if h.compression_rate <= 1.0 else int(h.compression_rate),
                        "lambda_value": h.lambda_value,
                        "category": h.category,
                        "date": h.date_crawled.strftime("%Y-%m-%d") if h.date_crawled else "",
                        "articles": [] # Not saved in DB
                    }
                db.close()
        except Exception as db_err:
            st.error(f"Gagal memuat detail dari database: {db_err}")
            
    if not cluster_data:
        st.error("Detail ringkasan tidak ditemukan.")
        st.markdown('<a href="?page=hasil" target="_self">Kembali ke Daftar Klaster</a>', unsafe_allow_html=True)
        st.stop()
        
    # Render Detail view
    # Back Button
    st.markdown(
        """
        <a href="?page=hasil" target="_self" style="display: inline-flex; align-items: center; gap: 8px; color: #707974; text-decoration: none; font-size: 14px; margin-bottom: 32px;" class="back-link">
            <span class="material-symbols-outlined" style="font-size: 18px;">arrow_back</span>
            Kembali ke Daftar Klaster
        </a>
        """,
        unsafe_allow_html=True
    )
    
    # Detail Column layout (Max reading width 768px)
    c_read1, c_read2, c_read3 = st.columns([1, 4, 1])
    with c_read2:
        # Header Metadata
        st.markdown(
            f"""
            <div style="margin-bottom: 48px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; font-size: 12px; font-weight: 700; color: #707974; text-transform: uppercase; letter-spacing: 0.1em;">
                    <span style="color: #064e3b; border-bottom: 2px solid #064e3b; padding-bottom: 4px;">KLASTER TOPiK</span>
                    <span>•</span>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <span class="material-symbols-outlined" style="font-size: 16px;">article</span>
                        <span>{cluster_data['article_count']} SUMBER</span>
                    </div>
                    <span>•</span>
                    <span>KOMPRESI: {cluster_data.get('compression_rate', 30)}%</span>
                    <span>•</span>
                    <span>LAMBDA: {cluster_data.get('lambda_value', 0.7)}</span>
                    {f"<span>•</span><span>Kategori: {cluster_data['category']}</span>" if 'category' in cluster_data else ''}
                    {f"<span>•</span><span>Tanggal: {cluster_data['date']}</span>" if 'date' in cluster_data else ''}
                </div>
                <h1 style="font-size: 42px; line-height: 1.2; font-family: 'Newsreader', serif; font-weight: 700; color: #003527; margin: 0;">
                    {cluster_data['topic_title']}
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Summary Content paragraphs
        paragraphs = split_summary_into_paragraphs(cluster_data['summary'], sentences_per_paragraph=3)
        for p in paragraphs:
            st.markdown(
                f"""
                <p style="font-size: 19px; line-height: 1.8; color: #404944; font-weight: 400; margin-bottom: 24px; font-family: 'Inter', sans-serif; text-align: justify;">
                    {p}
                </p>
                """,
                unsafe_allow_html=True
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Source articles reference list
        if cluster_data.get('articles'):
            st.markdown(
                """
                <div style="border-t: 0.5px solid rgba(191, 201, 195, 0.6); padding-top: 32px; margin-top: 48px; margin-bottom: 48px;">
                    <h3 style="font-size: 12px; font-weight: 600; color: #404944; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 24px;">Daftar Sumber Referensi:</h3>
                    <ul style="list-style-type: none; padding-left: 0; margin: 0; display: flex; flex-direction: column; gap: 12px;">
                """,
                unsafe_allow_html=True
            )
            for art in cluster_data['articles']:
                st.markdown(
                    f"""
                    <li style="font-size: 14px;">
                        <a href="{art['url']}" target="_blank" style="color: #707974; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: color 0.2s;">
                            <span class="material-symbols-outlined" style="font-size: 16px;">link</span>
                            <span style="border-bottom: 0.5px solid transparent;" onmouseover="this.style.color='#064e3b'; this.style.borderBottomColor='#064e3b';" onmouseout="this.style.color='#707974'; this.style.borderBottomColor='transparent';">{art['title']}</span>
                        </a>
                    </li>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown("</ul></div>", unsafe_allow_html=True)
            
        # Copy to Clipboard and Export Action Bar
        st.markdown("<hr style='border-color: #bfc9c3; margin-top: 40px;'>", unsafe_allow_html=True)
        
        col_act1, col_act2 = st.columns([1, 1])
        with col_act1:
            st.markdown(
                """
                <div style="font-size: 14px; color: #707974; padding-top: 10px;">
                    Dihasilkan oleh Pre-Trained SBERT Model
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_act2:
            st.markdown(
                """
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                """,
                unsafe_allow_html=True
            )
            
            # Since standard JavaScript clipboards inside Streamlit components have sandbox rules,
            # we will print a copy block at the bottom. We also render copy using st.code in an expander.
            copy_expander = st.expander("Salin Teks Ringkasan")
            with copy_expander:
                st.code(cluster_data['summary'], language="text")
                
            # Text download button
            st.download_button(
                label="Ekspor Teks",
                data=cluster_data['summary'],
                file_name=f"Berinkin_Ringkasan_{cluster_data['topic_title'].replace(' ', '_')[:35]}.txt",
                mime="text/plain",
                use_container_width=True
            )

# Close main content div
st.markdown('</div>', unsafe_allow_html=True)
