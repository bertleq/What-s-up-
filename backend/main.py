from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, Article, User, Interaction, init_db
from recommender import get_recommendations, update_matrix_factorization
from llm_service import answer_query
import json

app = FastAPI(title="News Reels App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    init_db()
    # Ensure index is fresh
    from search_engine import search_engine
    search_engine.refresh_index()

@app.get("/")
def read_root():
    return {"message": "Welcome to the News Reels API"}

@app.get("/feed")
def get_feed(user_id: int = 1, db: Session = Depends(get_db)):
    """
    Returns a list of articles tailored for the user.
    """
    # Ensure user exists (simple auto-create for demo)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username=f"user_{user_id}", preferences_vector="[]")
        db.add(user)
        db.commit()

    article_ids = get_recommendations(user_id)
    
    # Fetch full article objects
    articles = db.query(Article).filter(Article.id.in_(article_ids)).all()
    
    # Sort by the order returned by recommender (which is sorted by score)
    # Create a map for O(1) lookup
    article_map = {a.id: a for a in articles}
    ordered_articles = [article_map[aid] for aid in article_ids if aid in article_map]
    
    return ordered_articles

@app.get("/article/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

from search_engine import search_engine

@app.get("/search")
def search(query: str, db: Session = Depends(get_db)):
    """
    Semantic search + LLM answer.
    Uses BM25 for retrieval.
    """
    # BM25 Search
    results = search_engine.search(query, top_k=5)
    
    context = [{"title": a.title, "summary": a.long_summary,"url": a.url} for a in results]
    
    answer = answer_query(query, context)
    
    return {
        "answer": answer,
        "related_articles": results
    }

@app.post("/interact")
def record_interaction(user_id: int, article_id: int, action: str, db: Session = Depends(get_db)):
    if action not in ["view", "click", "like", "swipe_past"]:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    interaction = Interaction(user_id=user_id, article_id=article_id, action=action)
    db.add(interaction)
    db.commit()
    
    # Trigger re-calc periodically or async
    # For this demo, we'll trigger it every 5 interactions to show dynamic updates
    count = db.query(Interaction).count()
    if count % 5 == 0:
        update_matrix_factorization()
        print("Triggered matrix factorization update.")
    
    print(f"Recorded interaction: User {user_id} -> Article {article_id} ({action})")
    
    return {"status": "success"}

@app.post("/trigger-update")
def trigger_update():
    """
    Manually trigger matrix factorization update.
    """
    update_matrix_factorization()
    return {"status": "update started"}


"""
source venv/bin/activate && uvicorn backend.main:app --reload --port 8000
"""