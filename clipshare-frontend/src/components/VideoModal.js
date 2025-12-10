import React from 'react';
import { formatDate } from '../utils/dateFormatter';
import { likeVideo } from '../utils/api';

const VideoModal = ({ video, onClose, onVideoUpdate }) => {
  if (!video) return null;

  const handleLike = async () => {
    try {
      const data = await likeVideo(video.id);
      onVideoUpdate(video.id, { likes: data.likes });
    } catch (error) {
      console.error('Like error:', error);
    }
  };

  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close" onClick={onClose}>
          ✕
        </button>
        <video controls autoPlay src={video.videoUrl} />
        <div className="modal-info">
          <h2>{video.title}</h2>
          {video.description && <p>{video.description}</p>}
          <div className="stats">
            <span>👁️ {video.views || 0}</span>
            <button onClick={handleLike}>❤️ {video.likes || 0}</button>
            <span>{formatDate(video.createdAt)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoModal;

