import numpy as np
from database import SessionLocal, Article, User, Interaction
from sqlalchemy.orm import Session
import json

def update_matrix_factorization():
    """
    Re-computes the latent vectors for users and articles based on interactions.
    This is a simplified implementation using SVD.
    """
    print("Updating matrix factorization...")
    session = SessionLocal()
    
    # Fetch all interactions
    interactions = session.query(Interaction).all()
    if not interactions:
        print("No interactions found. Skipping update.")
        session.close()
        return

    # Map users and articles to matrix indices
    user_ids = sorted(list(set([i.user_id for i in interactions])))
    article_ids = sorted(list(set([i.article_id for i in interactions])))
    
    user_map = {uid: i for i, uid in enumerate(user_ids)}
    article_map = {aid: i for i, aid in enumerate(article_ids)}
    
    n_users = len(user_ids)
    n_articles = len(article_ids)
    
    # Build interaction matrix
    R = np.zeros((n_users, n_articles))
    for i in interactions:
        u_idx = user_map.get(i.user_id)
        a_idx = article_map.get(i.article_id)
        
        score = 0
        if i.action == "view": score = 1
        elif i.action == "click": score = 5
        elif i.action == "like": score = 10
        elif i.action == "swipe_past": score = -1
        
        if u_idx is not None and a_idx is not None:
            R[u_idx, a_idx] = score
            
    # Perform SVD (Simplified Matrix Factorization)
    # In a real app, use a proper library like Surprise or implicit
    try:
        U, S, Vt = np.linalg.svd(R, full_matrices=False)
        k = min(5, len(S)) # Latent dimension
        
        U_k = U[:, :k]
        S_k = np.diag(S[:k])
        V_k = Vt[:k, :]
        
        user_features = np.dot(U_k, S_k)
        article_features = V_k.T
        
        # Save back to DB
        for u_idx, uid in enumerate(user_ids):
            user = session.query(User).filter(User.id == uid).first()
            if user:
                user.preferences_vector = json.dumps(user_features[u_idx].tolist())
        
        for a_idx, aid in enumerate(article_ids):
            article = session.query(Article).filter(Article.id == aid).first()
            if article:
                article.vector = json.dumps(article_features[a_idx].tolist())
                
        session.commit()
        print("Matrix factorization updated.")
        
    except Exception as e:
        print(f"Error in matrix factorization: {e}")
        
    session.close()

def get_recommendations(user_id: int, limit: int = 10):
    """
    Returns a list of article IDs recommended for the user.
    """
    session = SessionLocal()
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user or not user.preferences_vector:
        # Cold start: return latest articles
        latest = session.query(Article).order_by(Article.published_at.desc()).limit(limit).all()
        session.close()
        return [a.id for a in latest]
        
    user_vec = np.array(json.loads(user.preferences_vector))
    
    # Get all articles with vectors
    articles = session.query(Article).filter(Article.vector != None).all()
    scores = []
    
    for a in articles:
        try:
            a_vec = np.array(json.loads(a.vector))
            if len(a_vec) == len(user_vec):
                score = np.dot(user_vec, a_vec)
                scores.append((a.id, score))
        except:
            pass
            
    # Sort by score
    scores.sort(key=lambda x: x[1], reverse=True)
    session.close()
    
    return [s[0] for s in scores[:limit]]

