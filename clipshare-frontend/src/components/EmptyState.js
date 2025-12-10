import React from 'react';

const EmptyState = ({ message = 'No videos yet. Upload one!' }) => {
  return <div className="empty">{message}</div>;
};

export default EmptyState;

