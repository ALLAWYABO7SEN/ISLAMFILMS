import React, { useState } from 'react';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedMovie, setSelectedMovie] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });
      
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('خطأ في البحث:', error);
      setSearchResults({ error: 'حدث خطأ أثناء البحث' });
    }
    setLoading(false);
  };

  const handleMovieSelect = async (movieId) => {
    setLoading(true);
    try {
      const response = await fetch('/api/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ movieId }),
      });
      
      const data = await response.json();
      setSelectedMovie(data);
    } catch (error) {
      console.error('خطأ في التقييم:', error);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="logo-container">
          <h1 className="logo">ISLAMFILMS</h1>
          <p className="tagline">تقييم الأفلام وفقاً للشريعة الإسلامية</p>
        </div>
        
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-container">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="ابحث عن فيلم أو مسلسل..."
              className="search-input"
              disabled={loading}
            />
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? 'جاري البحث...' : 'بحث'}
            </button>
          </div>
        </form>

        {searchResults && !selectedMovie && (
          <div className="results-container">
            {searchResults.error ? (
              <div className="error-message">{searchResults.error}</div>
            ) : searchResults.multiple ? (
              <div className="multiple-results">
                <h3>عُثر على عدة نتائج، يرجى الاختيار:</h3>
                <div className="movie-list">
                  {searchResults.movies.map((movie, index) => (
                    <button
                      key={index}
                      onClick={() => handleMovieSelect(movie.id)}
                      className="movie-option"
                    >
                      <div className="movie-title">{movie.title}</div>
                      <div className="movie-year">{movie.year}</div>
                      <div className="movie-type">{movie.type}</div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="single-result">
                <button
                  onClick={() => handleMovieSelect(searchResults.movie.id)}
                  className="movie-option single"
                >
                  <div className="movie-title">{searchResults.movie.title}</div>
                  <div className="movie-year">{searchResults.movie.year}</div>
                  <div className="movie-type">{searchResults.movie.type}</div>
                </button>
              </div>
            )}
          </div>
        )}

        {selectedMovie && (
          <div className="evaluation-container">
            <div className="movie-info">
              <h2>{selectedMovie.title}</h2>
              <p className="movie-details">{selectedMovie.year} • {selectedMovie.type}</p>
            </div>

            <div className="evaluation-results">
              <div className="score-container">
                <div className="overall-score">
                  <span className="score-number">{selectedMovie.overallScore}</span>
                  <span className="score-total">/100</span>
                </div>
                <p className="score-label">التقييم الإجمالي</p>
              </div>

              <div className="criteria-grid">
                {selectedMovie.criteria.map((criterion, index) => (
                  <div key={index} className="criterion-item">
                    <div className="criterion-header">
                      <span className="criterion-name">{criterion.name}</span>
                      <span className={`criterion-status ${criterion.status}`}>
                        {criterion.status === 'pass' ? '✓' : '✗'}
                      </span>
                    </div>
                    <p className="criterion-description">{criterion.description}</p>
                  </div>
                ))}
              </div>

              <div className="advice-section">
                <h3>النصائح والتوجيهات</h3>
                <div className="advice-item">
                  <h4>نصيحة عامة</h4>
                  <p>{selectedMovie.generalAdvice}</p>
                </div>
                <div className="advice-item">
                  <h4>تذكير ديني</h4>
                  <p>{selectedMovie.religiousReminder}</p>
                </div>
              </div>

              <div className="fatwa-section">
                <h3>الفتوى الشرعية</h3>
                <div className="fatwa-content">
                  {selectedMovie.fatwa}
                </div>
              </div>
            </div>

            <button 
              onClick={() => {
                setSelectedMovie(null);
                setSearchResults(null);
                setSearchQuery('');
              }}
              className="back-button"
            >
              بحث جديد
            </button>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;

