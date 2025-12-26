import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Search.css';

const Search = () => {
    const [query, setQuery] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            const response = await axios.get('http://localhost:8000/search', {
                params: { query: query }
            });
            setResult(response.data);
        } catch (error) {
            console.error("Error searching:", error);
        }
        setLoading(false);
    };

    return (
        <div className="search-container">
            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question about the news..."
                    className="search-input"
                />
                <button type="submit" className="search-button" disabled={loading}>
                    {loading ? '...' : 'Ask'}
                </button>
            </form>

            <div className="search-results">
                {result && (
                    <>
                        <div className="llm-answer">
                            <h3>AI Answer</h3>
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.answer}</ReactMarkdown>
                        </div>

                        <div className="related-articles">
                            <h3>Sources</h3>
                            {result.related_articles.map(article => (
                                <div key={article.id} className="related-card">
                                    <h4>{article.title}</h4>
                                    <p>{article.short_summary}</p>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default Search;
