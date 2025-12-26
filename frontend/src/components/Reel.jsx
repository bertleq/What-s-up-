import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import NewsCard from './NewsCard';
import './Reel.css';

const Reel = () => {
    const [articles, setArticles] = useState([]);
    const [loading, setLoading] = useState(true);
    const containerRef = useRef(null);

    useEffect(() => {
        fetchFeed();
    }, []);

    const fetchFeed = async () => {
        try {
            // Assuming backend is running on localhost:8000
            const response = await axios.get('http://localhost:8000/feed?user_id=1');
            setArticles(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching feed:", error);
            setLoading(false);
        }
    };

    const handleInteract = async (articleId, action) => {
        try {
            await axios.post('http://localhost:8000/interact', null, {
                params: {
                    user_id: 1,
                    article_id: articleId,
                    action: action
                }
            });
        } catch (error) {
            console.error("Error recording interaction:", error);
        }
    };

    if (loading) return <div className="loading">Loading feed...</div>;

    return (
        <div className="reel-container" ref={containerRef}>
            {articles.map((article) => (
                <NewsCard
                    key={article.id}
                    article={article}
                    onInteract={handleInteract}
                />
            ))}
            {articles.length === 0 && (
                <div className="empty-state">No articles found. Try running the scraper!</div>
            )}
        </div>
    );
};

export default Reel;
