from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import logging

app = Flask(__name__)
CORS(app)  # Ensure this is set up to handle CORS

# Directory to save downloaded videos
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url')

        if not url:
            raise ValueError("URL is required")

        # Define file path
        file_path = os.path.join(DOWNLOAD_DIR, 'video.mp4')

        # Download video
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)

        # Return the file path for download
        return jsonify({'status': 'success', 'file': file_path}), 200

    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except yt_dlp.utils.DownloadError as de:
        logging.error(f"DownloadError: {de}")
        return jsonify({'error': 'Failed to download video'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
