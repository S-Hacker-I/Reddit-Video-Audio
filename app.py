from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import logging

app = Flask(__name__)
CORS(app)  # Allow all origins, adjust as needed

# Set up logging
logging.basicConfig(level=logging.INFO)

DOWNLOAD_DIR = '/path/to/download/directory'

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        file_path = os.path.join(DOWNLOAD_DIR, 'video.mp4')

        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
        
        return jsonify({'status': 'success', 'file': 'video.mp4'}), 200

    except yt_dlp.utils.DownloadError as de:
        logging.error(f"DownloadError: {de}")
        return jsonify({'error': 'Failed to download video'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)  # Adjust port as needed
