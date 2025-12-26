from rank_bm25 import BM25Okapi
from database import SessionLocal, Article
import string

class SearchEngine:
    def __init__(self):
        self.bm25 = None
        self.articles = []
        self.article_ids = []
        self.refresh_index()

    def tokenize(self, text):
        # Simple tokenization: lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.split()

    def refresh_index(self):
        print("Refreshing search index...")
        session = SessionLocal()
        self.articles = session.query(Article).all()
        session.close()

        if not self.articles:
            print("No articles to index.")
            return

        # Indexing title + long_summary
        corpus = [
            self.tokenize(f"{a.title} {a.long_summary}") 
            for a in self.articles
        ]
        
        self.bm25 = BM25Okapi(corpus)
        self.article_ids = [a.id for a in self.articles]
        print(f"Indexed {len(self.articles)} articles.")

    def search(self, query, top_k=5):
        if not self.bm25:
            self.refresh_index()
            if not self.bm25:
                return []

        tokenized_query = self.tokenize(query)
        # Get scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Sort by score
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        # Filter out zero scores (irrelevant)
        results = []
        for i in top_n:
            if scores[i] > 0:
                results.append(self.articles[i])
                
        return results

# Global instance
search_engine = SearchEngine()
