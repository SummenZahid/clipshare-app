import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import Header from './components/Header';
import UploadForm from './components/UploadForm';
import SearchBar from './components/SearchBar';
import VideoGrid from './components/VideoGrid';
import VideoModal from './components/VideoModal';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import EmptyState from './components/EmptyState';
import Footer from './components/Footer';
import { fetchVideos, fetchStats } from './utils/api';

function App() {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);

  const loadVideos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const videosData = await fetchVideos();
      setVideos(videosData);
    } catch (error) {
      setError(`Failed to load videos.`);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const statsData = await fetchStats();
      setStats(statsData);
    } catch (error) {
      console.error('Stats error:', error);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    await Promise.all([loadVideos(), loadStats()]);
  }, [loadVideos, loadStats]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);


  const handleUploadSuccess = () => {
    loadInitialData();
  };

  const handleSearchResults = (results) => {
    setVideos(results);
  };

  const handleSearchClear = () => {
    loadVideos();
  };

  const handleVideoSelect = (video) => {
    setSelectedVideo(video);
    // Update the video in the list to reflect the view count
    setVideos(prevVideos =>
      prevVideos.map(v =>
        v.id === video.id ? { ...v, views: (v.views || 0) + 1 } : v
      )
    );
  };

  const handleVideoUpdate = (videoId, updates) => {
    setVideos(prevVideos =>
      prevVideos.map(v => (v.id === videoId ? { ...v, ...updates } : v))
    );
    if (selectedVideo && selectedVideo.id === videoId) {
      setSelectedVideo({ ...selectedVideo, ...updates });
    }
  };

  return (
    <div className="App">
      <Header stats={stats} />

      <main>
        <UploadForm onUploadSuccess={handleUploadSuccess} />

        <SearchBar
          onSearchResults={handleSearchResults}
          onClear={handleSearchClear}
        />

        <section className="videos">
          <h2>
            🎥 Videos <button onClick={loadVideos}>🔄</button>
          </h2>

          {loading && <LoadingSpinner />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && videos.length === 0 && <EmptyState />}
          {!loading && !error && videos.length > 0 && (
            <VideoGrid
              videos={videos}
              onVideoSelect={handleVideoSelect}
              onVideoUpdate={handleVideoUpdate}
            />
          )}
        </section>
      </main>

      {selectedVideo && (
        <VideoModal
          video={selectedVideo}
          onClose={() => setSelectedVideo(null)}
          onVideoUpdate={handleVideoUpdate}
        />
      )}

      <Footer />
    </div>
  );
}

export default App;
