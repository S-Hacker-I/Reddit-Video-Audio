from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Reddit Video Downloader is running!"}), 200

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Force the URL to use old.reddit.com for compatibility
    if 'reddit.com' in url:
        url = url.replace('www.reddit.com', 'old.reddit.com')

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'noplaylist': True,
        'extractor_retries': 3,
        'merge_output_format': 'mp4',  # Force output as mp4 for easier playback
    }

    try:
        # Use yt-dlp to download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
            video_filename = video_filename.replace('.webm', '.mp4')  # Ensure output is mp4
            
            # Return the downloaded video as an attachment
            return send_file(video_filename, as_attachment=True, attachment_filename='video.mp4')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Default port or from environment
    app.run(debug=True, host='0.0.0.0', port=port)
