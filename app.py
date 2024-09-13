from flask import Flask, request, jsonify, send_from_directory
import logging
import yt_dlp
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create downloads directory if not exists
os.makedirs('downloads', exist_ok=True)

@app.route('/')
def index():
    return "Welcome to the Reddit Video Downloader Service!"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            logging.error("URL is missing in request.")
            return jsonify({'error': 'URL is required'}), 400
        
        # Use yt-dlp to process the URL
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
        
        logging.info("Download successful.")
        return jsonify({'status': 'success', 'result': result}), 200
    
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except yt_dlp.utils.DownloadError as de:
        logging.error(f"DownloadError: {de}")
        return jsonify({'error': 'Failed to download video'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
