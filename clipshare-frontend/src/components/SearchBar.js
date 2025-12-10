import React, { useState } from 'react';
import { searchVideos } from '../utils/api';

const SearchBar = ({ onSearchResults, onClear }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) {
      onClear();
      return;
    }
    try {
      const results = await searchVideos(searchTerm);
      onSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    onClear();
  };

  return (
    <section className="search">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="🔍 Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button type="submit">Search</button>
        {searchTerm && (
          <button type="button" onClick={handleClear}>
            Clear
          </button>
        )}
      </form>
    </section>
  );
};

export default SearchBar;

