import { API_BASE_URL } from '../constants/api';

export const fetchVideos = async () => {
  const response = await fetch(`${API_BASE_URL}/videos`);
  if (!response.ok) throw new Error('Failed to fetch');
  const data = await response.json();
  return data.videos || [];
};

export const fetchStats = async () => {
  const response = await fetch(`${API_BASE_URL}/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return await response.json();
};

export const uploadVideo = async (formData) => {
  const response = await fetch(`${API_BASE_URL}/videos/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Upload failed');
  return await response.json();
};

export const likeVideo = async (videoId) => {
  const response = await fetch(`${API_BASE_URL}/videos/${videoId}/like`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Like failed');
  return await response.json();
};

export const searchVideos = async (query) => {
  const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
  if (!response.ok) throw new Error('Search failed');
  const data = await response.json();
  return data.results || [];
};

export const recordVideoView = async (videoId) => {
  try {
    await fetch(`${API_BASE_URL}/videos/${videoId}/view`, { method: 'POST' });
  } catch (error) {
    console.error('Failed to record view:', error);
  }
};

