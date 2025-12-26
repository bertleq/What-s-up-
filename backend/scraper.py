import requests
from bs4 import BeautifulSoup
import newspaper
from newspaper import Article as NewspaperArticle
import praw
import time
import os
from database import SessionLocal, Article
from sqlalchemy.exc import IntegrityError
import datetime
from llm_service import summarize_text

def scrape_news_sites():
    print("Scraping news sites...")
    # Example sources - in a real app, this list would be larger or dynamic
    urls = [
        "https://www.bbc.com/news",
        "https://edition.cnn.com",
        "https://www.theguardian.com/europe",
        "https://www.francetvinfo.fr/",
    ]
    
    session = SessionLocal()
    
    for url in urls:
        try:
            paper = newspaper.build(url, memoize_articles=False, number_threads=10)
            # Limit to first 5 for demo purposes to avoid long processing
            for article in paper.articles[:100]:
                try:
                    article.download()
                    article.parse()
                    
                    # Check if exists
                    exists = session.query(Article).filter(Article.url == article.url).first()
                    if exists:
                        continue
                        
                    # Summarize
                    short_sum = summarize_text(article.text, "short")
                    long_sum = summarize_text(article.text, "long")
                    
                    new_article = Article(
                        title=article.title,
                        url=article.url,
                        source=url,
                        published_at=article.publish_date or datetime.datetime.utcnow(),
                        short_summary=short_sum,
                        long_summary=long_sum,
                        content=article.text,
                        vector="[]" # Placeholder
                    )
                    session.add(new_article)
                    session.commit()
                    print(f"Saved: {article.title}")
                except Exception as e:
                    print(f"Error processing article {article.url}: {e}")
                    session.rollback()
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    session.close()

def scrape_reddit():
    print("Scraping Reddit...")
    # Requires Reddit API credentials. 
    # If not provided, we skip or use a public JSON endpoint (less reliable but works without auth for simple tests)
    
    # For this demo, I will use a public JSON endpoint approach to avoid needing user credentials immediately,
    # but strictly speaking PRAW is better.
    # Let's try PRAW if env vars exist, else fallback or skip.
    
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = "NewsReelsApp/1.0"
    
    if not client_id or not client_secret:
        print("Reddit credentials not found. Skipping Reddit scrape.")
        return

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        subreddit = reddit.subreddit("news+technology+worldnews")
        session = SessionLocal()
        
        for submission in subreddit.hot(limit=10):
            exists = session.query(Article).filter(Article.url == submission.url).first()
            if exists:
                continue
                
            short_sum = summarize_text(submission.selftext or submission.title, "short")
            long_sum = summarize_text(submission.selftext or submission.title, "long")
            
            new_article = Article(
                title=submission.title,
                url=submission.url,
                source="reddit",
                published_at=datetime.datetime.fromtimestamp(submission.created_utc),
                short_summary=short_sum,
                long_summary=long_sum,
                content=submission.selftext or "",
                vector="[]"
            )
            session.add(new_article)
            session.commit()
            print(f"Saved Reddit: {submission.title}")
            
        session.close()
    except Exception as e:
        print(f"Error scraping Reddit: {e}")

def run_scraper():
    print("Running scraper...")
    scrape_news_sites()
    scrape_reddit()
    print("Scraper finished.")

if __name__ == "__main__":
    run_scraper()
