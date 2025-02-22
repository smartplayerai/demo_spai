from flask import Flask, request, jsonify
import requests
from supabase import create_client, Client
import subprocess
import os

app = Flask(__name__)

# Supabase Configuration
SUPABASE_URL = 'https://sgwbrhwnulxzukzoaeqo.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnd2JyaHdudWx4enVrem9hZXFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAwNzE5MTIsImV4cCI6MjA1NTY0NzkxMn0.A82iCDeP41Ie2-GoDOk8OTpxcqaBIsDMHSPJG5MFDs4'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ensure video storage directory exists
VIDEO_DIR = "demo_spai"
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.route('/process-video', methods=['POST'])
def process_video():
    try:
        data = request.json
        video_url = data.get('video_url')
        if not video_url:
            return jsonify({'error': 'Missing video URL'}), 400

        input_video_path = os.path.join(VIDEO_DIR, 'input_video.mp4')
        output_video_path = os.path.join(VIDEO_DIR, 'output_video.mp4')

        # Download the video
        video_response = requests.get(video_url)
        if video_response.status_code != 200:
            return jsonify({'error': 'Failed to download video'}), 400

        with open(input_video_path, 'wb') as f:
            f.write(video_response.content)

        # Run ball tracking code
        subprocess.run(['python', 'demo_spai/ball_tracking.py', input_video_path, output_video_path])

        # Upload processed video to Supabase
        with open(output_video_path, 'rb') as f:
            supabase.storage.from_('videos').upload('processed/output_video.mp4', f)

        # Get public URL of the processed video
        processed_video_url = supabase.storage.from_('videos').get_public_url('processed/output_video.mp4')

        return jsonify({'processed_video_url': processed_video_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
