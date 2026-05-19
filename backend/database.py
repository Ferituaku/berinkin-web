from sqlalchemy import create_engine, Column, String, Date, Integer, Text, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

import mysql.connector

MYSQL_URL = os.getenv("MYSQL_URL", "mysql+mysqlconnector://root:@localhost:3306/berinkin")

# Auto-create database if not exists
try:
    conn = mysql.connector.connect(host="localhost", user="root", password="")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS berinkin")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Warning: Could not auto-create database: {e}")

try:
    engine = create_engine(MYSQL_URL)
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
        Base.metadata.create_all(bind=engine)

def get_db():
    if not SessionLocal:
        raise Exception("Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
