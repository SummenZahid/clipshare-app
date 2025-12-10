# ClipShare - Video Sharing Platform

## Quick Start

### Backend (Flask)

```bash
cd clipshare-backend
pip install -r requirements.txt
python app.py
```

Backend runs on: http://localhost:8000

### Frontend (React)

```bash
cd clipshare-frontend
npm install
npm start
```

Frontend runs on: http://localhost:3000

## Docker Compose (All Services)

```bash
docker-compose -f docker/docker-compose.yml up --build
```

This starts both backend and frontend together.

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/videos` - List all videos
- `POST /api/videos/upload` - Upload video
- `GET /api/search?q=term` - Search videos
- `POST /api/videos/<id>/like` - Like video
- `POST /api/videos/<id>/view` - Increment views
- `GET /api/stats` - Platform statistics

