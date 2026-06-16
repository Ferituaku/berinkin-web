from sqlalchemy import create_engine, Column, String, Date, Integer, Text, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# ─────────────────────────────────────────────────────────────────────────────
# Database URL resolution
# Priority:
#   1. MYSQL_URL  env var  → uses MySQL (production / local with MySQL)
#   2. Fallback             → SQLite file stored next to this file (cloud-safe)
# ─────────────────────────────────────────────────────────────────────────────

MYSQL_URL = os.getenv("MYSQL_URL", "")

if MYSQL_URL:
    # ── MySQL path (requires mysql-connector-python) ──────────────────────────
    try:
        import mysql.connector
        # Auto-create database if it doesn't exist yet
        try:
            _cfg = {}
            # Parse minimal connection params from URL for auto-create
            _parts = MYSQL_URL.split("//")[-1]  # user:pass@host:port/db
            _auth, _rest = _parts.rsplit("@", 1)
            _user, _pass = (_auth.split(":", 1) + [""])[:2]
            _host_port, _dbname = _rest.rsplit("/", 1)
            _host = _host_port.split(":")[0]
            _port = int(_host_port.split(":")[1]) if ":" in _host_port else 3306
            conn = mysql.connector.connect(host=_host, port=_port, user=_user, password=_pass)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{_dbname}`")
            cursor.close()
            conn.close()
        except Exception as _e:
            print(f"Warning: Could not auto-create MySQL database: {_e}")
        DB_URL = MYSQL_URL
        print(f"[DB] Using MySQL: {MYSQL_URL.split('@')[-1]}")
    except ImportError:
        print("Warning: mysql-connector-python not installed. Falling back to SQLite.")
        MYSQL_URL = ""

if not MYSQL_URL:
    # ── SQLite fallback (zero config, works on Streamlit Cloud) ───────────────
    _db_dir = os.path.dirname(os.path.abspath(__file__))
    _db_path = os.path.join(_db_dir, "berinkin.db")
    DB_URL = f"sqlite:///{_db_path}"
    print(f"[DB] Using SQLite: {_db_path}")

# ─── SQLAlchemy engine & session ─────────────────────────────────────────────
try:
    _connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
    engine = create_engine(DB_URL, connect_args=_connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    engine = None
    SessionLocal = None
    print(f"Database connection failed: {e}")

Base = declarative_base()

class SummaryHistory(Base):
    __tablename__ = "summary_history"

    id = Column(String(36), primary_key=True, index=True)
    date_crawled = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)
    cluster_topic = Column(String(255), nullable=False)
    article_count = Column(Integer, default=1)
    summary_text = Column(Text, nullable=False)
    compression_rate = Column(Float, default=0.3)
    lambda_value = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    if engine:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            print(f"Database initialization failed (tables could not be created): {e}")

def get_db():
    if not SessionLocal:
        raise Exception("Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
