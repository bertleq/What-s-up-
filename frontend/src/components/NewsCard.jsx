import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './NewsCard.css';

const NewsCard = ({ article, onInteract }) => {
    const [expanded, setExpanded] = useState(false);
    const cardRef = useRef(null);
    const hasViewed = useRef(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !hasViewed.current) {
                    hasViewed.current = true;
                    onInteract(article.id, 'view');
                    console.log(`Viewed article ${article.id}`);
                }
            },
            { threshold: 0.6 }
        );

        if (cardRef.current) {
            observer.observe(cardRef.current);
        }

        return () => {
            if (cardRef.current) {
                observer.unobserve(cardRef.current);
            }
        };
    }, [article.id, onInteract]);

    const handleExpand = () => {
        setExpanded(!expanded);
        if (!expanded) {
            onInteract(article.id, 'click');
        }
    };

    return (
        <div className="news-card-container" ref={cardRef}>
            <div className="news-card" onClick={handleExpand}>
                <div className="content-wrapper">
                    <h1 className="big-title">{article.short_summary}</h1>
                    <p className="source">{article.source}</p>
                </div>
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        className="expanded-overlay"
                        initial={{ y: '100%' }}
                        animate={{ y: 0 }}
                        exit={{ y: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    >
                        <button className="close-btn" onClick={(e) => { e.stopPropagation(); setExpanded(false); }}>
                            &times;
                        </button>
                        <div className="expanded-content">
                            <h2>{article.title}</h2>
                            <div className="long-summary">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{article.long_summary}</ReactMarkdown>
                            </div>
                            <a href={article.url} target="_blank" rel="noopener noreferrer" className="read-more">
                                Read full article
                            </a>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default NewsCard;
