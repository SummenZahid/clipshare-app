import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'healthy'

def test_get_videos(client):
    response = client.get('/api/videos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'videos' in data

def test_get_stats(client):
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_videos' in data
    assert 'total_views' in data
    assert 'total_likes' in data

def test_search_videos(client):
    response = client.get('/api/search?q=test')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'results' in data

def test_like_video(client):
    videos_response = client.get('/api/videos')
    videos_data = json.loads(videos_response.data)
    
    if videos_data.get('videos') and len(videos_data['videos']) > 0:
        video_id = videos_data['videos'][0]['id']
        response = client.post(f'/api/videos/{video_id}/like')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'likes' in data
