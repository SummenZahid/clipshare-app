import React from 'react';
import VideoCard from './VideoCard';
import { likeVideo, recordVideoView } from '../utils/api';

const VideoGrid = ({ videos, onVideoSelect, onVideoUpdate }) => {
  const handleLike = async (videoId) => {
    try {
      const data = await likeVideo(videoId);
      onVideoUpdate(videoId, { likes: data.likes });
    } catch (error) {
      console.error('Like error:', error);
    }
  };

  const handleVideoClick = (video) => {
    recordVideoView(video.id);
    onVideoSelect(video);
  };

  return (
    <div className="grid">
      {videos.map((video) => (
        <VideoCard
          key={video.id}
          video={video}
          onVideoClick={handleVideoClick}
          onLike={handleLike}
        />
      ))}
    </div>
  );
};

export default VideoGrid;

