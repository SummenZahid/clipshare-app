import React from 'react';

const Header = ({ stats }) => {
  return (
    <header className="header">
      <h1>🎬 ClipShare</h1>
      <p>Cloud-Native Video Platform</p>
      {stats && (
        <div className="stats">
          <span>📹 {stats.total_videos}</span>
          <span>👁️ {stats.total_views}</span>
          <span>❤️ {stats.total_likes}</span>
          <span>{stats.storage_mode === 'Azure' ? '☁️ Azure' : '💾 Local'}</span>
        </div>
      )}
    </header>
  );
};

export default Header;

