import React, { useState } from 'react';
import Reel from './components/Reel';
import Search from './components/Search';
import './App.css';

function App() {
  const [view, setView] = useState('feed'); // 'feed' or 'search'

  return (
    <div className="app-container">
      {view === 'feed' && <Reel />}
      {view === 'search' && <Search />}

      <div className="bottom-nav">
        <button
          className={view === 'feed' ? 'active' : ''}
          onClick={() => setView('feed')}
        >
          Feed
        </button>
        <button
          className={view === 'search' ? 'active' : ''}
          onClick={() => setView('search')}
        >
          Search
        </button>
      </div>
    </div>
  );
}

export default App;
