from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import praw
import requests
import os
import tempfile
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Initialize the Reddit API client
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="YOUR_USER_AGENT"
)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    # Validate the URL
    if not url:
        return jsonify({"success": False, "error": "No URL provided."}), 400

    if not is_valid_reddit_url(url):
        return jsonify({"success": False, "error": "Invalid Reddit URL."}), 400

    try:
        # Download the video
        video_path = fetch_reddit_video(url)

        if video_path:
            return send_file(video_path, as_attachment=True, download_name='reddit_video.mp4')
        else:
            return jsonify({"success": False, "error": "Failed to retrieve video."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def is_valid_reddit_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc in ["www.reddit.com", "reddit.com", "old.reddit.com"]

def fetch_reddit_video(url):
    try:
        # Extract the submission ID from the URL
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        submission_id = next((part for part in path_parts if part.startswith('comments')), None)
        
        if not submission_id:
            raise ValueError("Invalid Reddit URL")

        # Fetch the submission
        submission = reddit.submission(id=submission_id)

        if not hasattr(submission, 'media') or not submission.media:
            raise ValueError("No media found in this post")

        # Extract video and audio URLs
        video_url = submission.media['reddit_video']['fallback_url']
        audio_url = video_url.split('DASH_')[0] + 'DASH_audio.mp4'

        # Download video and audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as video_file, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as audio_file:
            
            download_file(video_url, video_file.name)
            download_file(audio_url, audio_file.name)

            # Merge video and audio
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            merge_video_audio(video_file.name, audio_file.name, output_file.name)

        # Clean up temporary files
        os.unlink(video_file.name)
        os.unlink(audio_file.name)

        return output_file.name
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def merge_video_audio(video_path, audio_path, output_path):
    # You'll need to implement this function to merge video and audio
    # You can use ffmpeg-python or moviepy for this purpose
    # For simplicity, let's use a system call to ffmpeg
    os.system(f"ffmpeg -i {video_path} -i {audio_path} -c copy {output_path}")

if __name__ == '__main__':
    app.run(port=5000)
