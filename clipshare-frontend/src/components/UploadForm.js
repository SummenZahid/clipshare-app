import React, { useState, useRef } from 'react';
import { uploadVideo } from '../utils/api';

const UploadForm = ({ onUploadSuccess }) => {
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle.trim()) {
      alert('Please provide a title and select a video');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('video', uploadFile);
    formData.append('title', uploadTitle);
    formData.append('description', uploadDescription);
    formData.append('userId', 'user-' + Date.now());

    try {
      await uploadVideo(formData);
      alert('✅ Video uploaded!');
      setUploadFile(null);
      setUploadTitle('');
      setUploadDescription('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onUploadSuccess();
    } catch (error) {
      alert('❌ Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <section className="upload">
      <h2>📤 Upload Video</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Title *"
          value={uploadTitle}
          onChange={(e) => setUploadTitle(e.target.value)}
          required
        />
        <textarea
          placeholder="Description"
          value={uploadDescription}
          onChange={(e) => setUploadDescription(e.target.value)}
          rows="3"
        />
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={(e) => setUploadFile(e.target.files[0])}
          required
        />
        <button type="submit" disabled={uploading}>
          {uploading ? '⏳ Uploading...' : '🚀 Upload'}
        </button>
      </form>
    </section>
  );
};

export default UploadForm;

