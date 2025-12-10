import React from 'react';
import { formatDate } from '../utils/dateFormatter';

const VideoCard = ({ video, onVideoClick, onLike }) => {
  const handleLike = (e) => {
    e.stopPropagation();
    onLike(video.id);
  };

  return (
    <div className="card" onClick={() => onVideoClick(video)}>
      <div className="thumbnail">
        <div className="play">▶️</div>
        <video src={video.videoUrl} preload="metadata" />
      </div>
      <div className="info">
        <h3>{video.title}</h3>
        {video.description && <p>{video.description}</p>}
        <div className="stats">
          <span>👁️ {video.views || 0}</span>
          <button onClick={handleLike}>❤️ {video.likes || 0}</button>
        </div>
        <small>{formatDate(video.createdAt)}</small>
      </div>
    </div>
  );
};

export default VideoCard;

