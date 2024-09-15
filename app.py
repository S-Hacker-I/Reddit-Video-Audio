from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import logging
import os

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.before_request
def log_request_info():
    logging.debug(f"Request URL: {request.url}")
    logging.debug(f"Request Method: {request.method}")
    logging.debug(f"Request Headers: {request.headers}")
    logging.debug(f"Request Body: {request.get_data()}")

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            logging.error("No URL provided")
            return jsonify({'error': 'No URL provided'}), 400

        logging.info(f"Downloading video from URL: {video_url}")

        # Set up yt-dlp options for Reddit videos
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': False,
        }

        # Create a directory for downloads if it doesn't exist
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)

        logging.info(f"Video downloaded successfully: {filename}")

        return send_file(filename, as_attachment=True)

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Download error: {e}")
        return jsonify({'error': 'Failed to download video'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
