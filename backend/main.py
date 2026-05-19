from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
import datetime
import json

from database import init_db, get_db, SummaryHistory
from core.scraper import scrape_articles_pipeline_generator
from core.summarizer import summarize_pipeline_generator

app = FastAPI(title="Berinkin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to Berinkin API"}

class SummarizeRequest(BaseModel):
    category: str
    date: str
    max_articles: int
    compression: float
    lambda_param: float

@app.post("/api/summarize")
def summarize_topic(request: SummarizeRequest):
    print(f"Request: {request.category} on {request.date} with lambda {request.lambda_param}")
    
    def event_stream():
        articles = []
        
        # 1. Scrape data
        for update in scrape_articles_pipeline_generator(request.category, request.date, request.max_articles):
            if "results" in update:
                articles = update.pop("results")
            yield f"data: {json.dumps(update)}\n\n"
            
        if not articles:
            yield f"data: {json.dumps({'progress': 100, 'status': 'error', 'message': 'No articles found for the given category/date.'})}\n\n"
            return
            
        # 2. Summarize (Clustering & MMR)
        final_clusters = []
        for update in summarize_pipeline_generator(articles, compression_rate=request.compression, lambda_param=request.lambda_param):
            if "clusters" in update:
                final_clusters = update.pop("clusters")
                
                if final_clusters:
                    # Enrich clusters with config
                    for c in final_clusters:
                        c['compression_rate'] = request.compression
                        c['lambda_value'] = request.lambda_param
                    
                    update["status"] = "success"
                    update["clusters"] = final_clusters
                    
                    # 3. Save to database
                    try:
                        from database import SessionLocal
                        if SessionLocal:
                            db = SessionLocal()
                            for c in final_clusters:
                                history = SummaryHistory(
                                    id=str(uuid.uuid4()),
                                    date_crawled=datetime.datetime.strptime(request.date, "%Y-%m-%d").date() if "-" in request.date else datetime.date.today(),
                                    category=request.category,
                                    cluster_topic=c['topic_title'],
                                    article_count=c['article_count'],
                                    summary_text=c['summary'],
                                    compression_rate=c['compression_rate'],
                                    lambda_value=c['lambda_value']
                                )
                                db.add(history)
                            db.commit()
                            db.close()
                    except Exception as e:
                        print(f"Failed to save to database: {e}")
                else:
                    # Fallback if clustering resulted in 0 valid clusters
                    fallback_cluster = [{
                        "cluster_id": str(uuid.uuid4()),
                        "topic_title": articles[0]['title'],
                        "article_count": len(articles),
                        "summary": "Data insufficient to form a valid cluster of multiple articles. Try again.",
                        "articles": articles,
                        "compression_rate": request.compression,
                        "lambda_value": request.lambda_param
                    }]
                    update["status"] = "success"
                    update["clusters"] = fallback_cluster

            yield f"data: {json.dumps(update)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
