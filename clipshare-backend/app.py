from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import json

try:
    from azure.cosmos import CosmosClient, exceptions
    from azure.storage.blob import BlobServiceClient, ContentSettings
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from services.cognitive_services import get_video_insights, analyze_video_thumbnail, transcribe_video
    COGNITIVE_SERVICES_AVAILABLE = True
except ImportError:
    COGNITIVE_SERVICES_AVAILABLE = False

app = Flask(__name__)

# Configure CORS for deployment
CORS(
    app,
    resources={r"/api/*": {"origins": ["https://clipshare-frontend-summen-a6d5ghb2afc0fqb4.spaincentral-01.azurewebsites.net"]}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    supports_credentials=False,  # keep False unless you REALLY need cookies
    expose_headers=["Content-Range", "X-Content-Range"],
)

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)

USE_AZURE = False
if AZURE_AVAILABLE:
    COSMOS_ENDPOINT = os.environ.get('COSMOS_ENDPOINT')
    COSMOS_KEY = os.environ.get('COSMOS_KEY')
    STORAGE_CONNECTION_STRING = os.environ.get('STORAGE_CONNECTION_STRING')
    
    if COSMOS_ENDPOINT and COSMOS_KEY and STORAGE_CONNECTION_STRING:
        try:
            cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
            database = cosmos_client.get_database_client("clipsharedb")
            container = database.get_container_client("videos")
            blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
            USE_AZURE = True
        except Exception as e:
            print(f"Azure connection failed: {e}")
            USE_AZURE = False

LOCAL_DB_FILE = 'local_videos.json'

def load_local_db():
    if os.path.exists(LOCAL_DB_FILE):
        with open(LOCAL_DB_FILE, 'r') as f:
            return json.load(f)
    return []

def save_local_db(videos):
    with open(LOCAL_DB_FILE, 'w') as f:
        json.dump(videos, f, indent=2)

@app.route('/')
def index():
    return jsonify({
        'message': 'ClipShare API',
        'version': '1.0',
        'endpoints': {
            'health': '/api/health',
            'videos': '/api/videos',
            'upload': '/api/videos/upload',
            'search': '/api/search'
        },
        'mode': 'Azure' if USE_AZURE else 'Local',
        'status': 'running'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'mode': 'Azure' if USE_AZURE else 'Local Storage',
        'azure_connected': USE_AZURE
    })

@app.route('/api/videos', methods=['GET'])
def get_videos():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        if USE_AZURE:
            query = "SELECT * FROM c ORDER BY c.createdAt DESC"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
        else:
            items = load_local_db()
            items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_items = items[start:end]
        
        return jsonify({
            'videos': paginated_items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<video_id>', methods=['GET'])
def get_video(video_id):
    try:
        if USE_AZURE:
            query = f"SELECT * FROM c WHERE c.id = '{video_id}'"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if not items:
                return jsonify({'error': 'Video not found'}), 404
                
            return jsonify(items[0])
        else:
            videos = load_local_db()
            video = next((v for v in videos if v['id'] == video_id), None)
            
            if not video:
                return jsonify({'error': 'Video not found'}), 404
            
            return jsonify(video)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        
        if video_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        title = request.form.get('title', 'Untitled')
        description = request.form.get('description', '')
        user_id = request.form.get('userId', 'anonymous')
        
        video_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        if USE_AZURE:
            blob_name = f"{video_id}/{video_file.filename}"
            container_client = blob_service_client.get_container_client("videos")
            
            try:
                container_client.create_container()
            except:
                pass
            
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(
                video_file.read(),
                overwrite=True,
                content_settings=ContentSettings(content_type='video/mp4')
            )
            
            video_url = blob_client.url
            
            video_metadata = {
                'id': video_id,
                'userId': user_id,
                'title': title,
                'description': description,
                'videoUrl': video_url,
                'blobName': blob_name,
                'createdAt': timestamp,
                'views': 0,
                'likes': 0,
                'status': 'ready'
            }
            
            container.create_item(body=video_metadata)
            
        else:
            filename = f"{video_id}_{video_file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
            video_file.save(filepath)
            
            video_url = f"/uploads/videos/{filename}"
            
            video_metadata = {
                'id': video_id,
                'userId': user_id,
                'title': title,
                'description': description,
                'videoUrl': video_url,
                'filename': filename,
                'createdAt': timestamp,
                'views': 0,
                'likes': 0,
                'status': 'ready'
            }
            
            videos = load_local_db()
            videos.append(video_metadata)
            save_local_db(videos)
        
        insights = None
        if COGNITIVE_SERVICES_AVAILABLE and USE_AZURE:
            try:
                insights = get_video_insights(video_url, video_id, video_metadata)
                video_metadata.update({
                    'tags': insights.get('analysis', {}).get('tags', []),
                    'description_ai': insights.get('analysis', {}).get('description'),
                    'moderation_status': insights.get('moderation', {}).get('moderation_status', 'pending')
                })
                videos = load_local_db()
                for v in videos:
                    if v['id'] == video_id:
                        v.update(video_metadata)
                        break
                save_local_db(videos)
            except Exception as e:
                print(f"Cognitive Services error: {e}")
        
        response_data = {
            'message': 'Video uploaded successfully',
            'videoId': video_id,
            'videoUrl': video_url,
            'status': 'ready'
        }
        
        if insights:
            response_data['insights'] = {
                'tags': insights.get('analysis', {}).get('tags', []),
                'moderation_status': insights.get('moderation', {}).get('moderation_status')
            }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/videos/<filename>')
def serve_video(filename):
    return send_from_directory(
        os.path.join(app.config['UPLOAD_FOLDER'], 'videos'),
        filename
    )

@app.route('/api/videos/<video_id>/view', methods=['POST'])
def increment_view(video_id):
    try:
        if USE_AZURE:
            query = f"SELECT * FROM c WHERE c.id = '{video_id}'"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if not items:
                return jsonify({'error': 'Video not found'}), 404
            
            video = items[0]
            video['views'] = video.get('views', 0) + 1
            container.upsert_item(body=video)
            
        else:
            videos = load_local_db()
            video = next((v for v in videos if v['id'] == video_id), None)
            
            if not video:
                return jsonify({'error': 'Video not found'}), 404
            
            video['views'] = video.get('views', 0) + 1
            save_local_db(videos)
        
        return jsonify({'views': video['views']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<video_id>/like', methods=['POST'])
def like_video(video_id):
    try:
        if USE_AZURE:
            query = f"SELECT * FROM c WHERE c.id = '{video_id}'"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if not items:
                return jsonify({'error': 'Video not found'}), 404
            
            video = items[0]
            video['likes'] = video.get('likes', 0) + 1
            container.upsert_item(body=video)
            
        else:
            videos = load_local_db()
            video = next((v for v in videos if v['id'] == video_id), None)
            
            if not video:
                return jsonify({'error': 'Video not found'}), 404
            
            video['likes'] = video.get('likes', 0) + 1
            save_local_db(videos)
        
        return jsonify({'likes': video['likes']})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_videos():
    try:
        search_term = request.args.get('q', '').lower()
        
        if not search_term:
            return jsonify({'error': 'Search term required'}), 400
        
        if USE_AZURE:
            query = f"""
            SELECT * FROM c 
            WHERE CONTAINS(LOWER(c.title), '{search_term}')
               OR CONTAINS(LOWER(c.description), '{search_term}')
            ORDER BY c.createdAt DESC
            """
            
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
        else:
            videos = load_local_db()
            items = [
                v for v in videos 
                if search_term in v.get('title', '').lower() 
                or search_term in v.get('description', '').lower()
            ]
        
        return jsonify({
            'results': items,
            'count': len(items),
            'search_term': search_term
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<video_id>/analyze', methods=['POST'])
def analyze_video(video_id):
    try:
        if not COGNITIVE_SERVICES_AVAILABLE:
            return jsonify({'error': 'Cognitive Services not available'}), 503
        
        if USE_AZURE:
            query = f"SELECT * FROM c WHERE c.id = '{video_id}'"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            if not items:
                return jsonify({'error': 'Video not found'}), 404
            video = items[0]
        else:
            videos = load_local_db()
            video = next((v for v in videos if v['id'] == video_id), None)
            if not video:
                return jsonify({'error': 'Video not found'}), 404
        
        insights = get_video_insights(video.get('videoUrl'), video_id, video)
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<video_id>/transcript', methods=['GET'])
def get_transcript(video_id):
    try:
        if not COGNITIVE_SERVICES_AVAILABLE:
            return jsonify({'error': 'Cognitive Services not available'}), 503
        
        if USE_AZURE:
            query = f"SELECT * FROM c WHERE c.id = '{video_id}'"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            if not items:
                return jsonify({'error': 'Video not found'}), 404
            video = items[0]
        else:
            videos = load_local_db()
            video = next((v for v in videos if v['id'] == video_id), None)
            if not video:
                return jsonify({'error': 'Video not found'}), 404
        
        transcription = transcribe_video(video.get('videoUrl'), video_id)
        
        if not transcription:
            return jsonify({'error': 'Transcription not available'}), 404
        
        return jsonify(transcription)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        if USE_AZURE:
            query = "SELECT * FROM c"
            videos = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
        else:
            videos = load_local_db()
        
        total_views = sum(v.get('views', 0) for v in videos)
        total_likes = sum(v.get('likes', 0) for v in videos)
        
        stats_data = {
            'total_videos': len(videos),
            'total_views': total_views,
            'total_likes': total_likes,
            'storage_mode': 'Azure' if USE_AZURE else 'Local',
            'cognitive_services_enabled': COGNITIVE_SERVICES_AVAILABLE
        }
        
        return jsonify(stats_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 500MB'}), 413

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
