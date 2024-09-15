from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Directory to temporarily store video files
VIDEO_DIR = 'videos'
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Define download options
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Try to get the best video and audio combination
        'outtmpl': os.path.join(VIDEO_DIR, 'video.mp4'),
        'noplaylist': True,
        'quiet': False,  # Set to False for debugging
        'writethumbnail': True,  # Optionally write the thumbnail
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract info to list formats before downloading
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            
            # Print available formats for debugging
            print("Available formats:")
            for f in formats:
                print(f"{f['format_id']}: {f['ext']} - {f.get('resolution', 'N/A')}")

            # Download the video
            ydl.download([url])
        except Exception as e:
            # Print the error message for debugging
            print(f"Error: {e}")
            return jsonify({'error': str(e)}), 500

    video_path = os.path.join(VIDEO_DIR, 'video.mp4')
    if not os.path.isfile(video_path):
        return jsonify({'error': 'Video file was not created'}), 500

    return send_file(video_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
