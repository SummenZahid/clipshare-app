import os
from typing import Dict, Optional
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
import requests
import time

COGNITIVE_SERVICES_KEY = os.environ.get('COGNITIVE_SERVICES_KEY')
COGNITIVE_SERVICES_ENDPOINT = os.environ.get('COGNITIVE_SERVICES_ENDPOINT')
VIDEO_INDEXER_KEY = os.environ.get('VIDEO_INDEXER_KEY')
VIDEO_INDEXER_ACCOUNT_ID = os.environ.get('VIDEO_INDEXER_ACCOUNT_ID')
VIDEO_INDEXER_LOCATION = os.environ.get('VIDEO_INDEXER_LOCATION', 'trial')

def analyze_video_thumbnail(video_url: str) -> Optional[Dict]:
    if not COGNITIVE_SERVICES_KEY or not COGNITIVE_SERVICES_ENDPOINT:
        return None
    
    try:
        client = ComputerVisionClient(COGNITIVE_SERVICES_ENDPOINT, COGNITIVE_SERVICES_KEY)
        analysis = client.analyze_image(video_url, visual_features=['Tags', 'Description', 'Adult', 'Objects'])
        
        return {
            'tags': [tag.name for tag in analysis.tags],
            'description': analysis.description.captions[0].text if analysis.description.captions else None,
            'is_adult_content': analysis.adult.is_adult_content,
            'is_racy_content': analysis.adult.is_racy_content,
            'objects': [obj.object_property for obj in analysis.objects] if hasattr(analysis, 'objects') else []
        }
    except Exception as e:
        print(f"Computer Vision API error: {e}")
        return None

def transcribe_video(video_url: str, video_id: str) -> Optional[Dict]:
    if not VIDEO_INDEXER_KEY or not VIDEO_INDEXER_ACCOUNT_ID:
        return None
    
    try:
        access_token_url = f"https://api.videoindexer.ai/auth/{VIDEO_INDEXER_LOCATION}/Accounts/{VIDEO_INDEXER_ACCOUNT_ID}/AccessToken"
        headers = {'Ocp-Apim-Subscription-Key': VIDEO_INDEXER_KEY}
        response = requests.get(access_token_url, headers=headers, params={'allowEdit': 'true'})
        access_token = response.json()
        
        index_url = f"https://api.videoindexer.ai/{VIDEO_INDEXER_LOCATION}/Accounts/{VIDEO_INDEXER_ACCOUNT_ID}/Videos"
        params = {
            'accessToken': access_token,
            'name': video_id,
            'videoUrl': video_url,
            'language': 'en-US'
        }
        
        upload_response = requests.post(index_url, params=params)
        video_indexer_id = upload_response.json().get('id')
        
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(5)
            status_url = f"https://api.videoindexer.ai/{VIDEO_INDEXER_LOCATION}/Accounts/{VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_indexer_id}/Index"
            status_response = requests.get(status_url, params={'accessToken': access_token})
            status = status_response.json().get('state')
            
            if status == 'Processed':
                transcript_url = f"https://api.videoindexer.ai/{VIDEO_INDEXER_LOCATION}/Accounts/{VIDEO_INDEXER_ACCOUNT_ID}/Videos/{video_indexer_id}/Transcript"
                transcript_response = requests.get(transcript_url, params={'accessToken': access_token})
                transcript_data = transcript_response.json()
                
                return {
                    'transcript': transcript_data.get('text', ''),
                    'words': transcript_data.get('words', []),
                    'video_indexer_id': video_indexer_id
                }
            elif status == 'Failed':
                return None
        
        return None
    except Exception as e:
        print(f"Video Indexer API error: {e}")
        return None

def moderate_content(video_metadata: Dict, thumbnail_analysis: Optional[Dict]) -> Dict:
    flags = []
    is_safe = True
    
    if thumbnail_analysis:
        if thumbnail_analysis.get('is_adult_content'):
            flags.append('adult_content')
            is_safe = False
        if thumbnail_analysis.get('is_racy_content'):
            flags.append('racy_content')
    
    inappropriate_keywords = ['spam', 'fake', 'scam']
    title = video_metadata.get('title', '').lower()
    description = video_metadata.get('description', '').lower()
    
    for keyword in inappropriate_keywords:
        if keyword in title or keyword in description:
            flags.append('inappropriate_keywords')
            is_safe = False
            break
    
    return {
        'is_safe': is_safe,
        'flags': flags,
        'moderation_status': 'approved' if is_safe else 'flagged'
    }

def get_video_insights(video_url: str, video_id: str, video_metadata: Dict) -> Dict:
    insights = {
        'video_id': video_id,
        'analysis': {},
        'transcription': None,
        'moderation': {}
    }
    
    thumbnail_analysis = analyze_video_thumbnail(video_url)
    if thumbnail_analysis:
        insights['analysis'] = thumbnail_analysis
    
    transcription = transcribe_video(video_url, video_id)
    if transcription:
        insights['transcription'] = transcription
    
    moderation = moderate_content(video_metadata, thumbnail_analysis)
    insights['moderation'] = moderation
    
    return insights
