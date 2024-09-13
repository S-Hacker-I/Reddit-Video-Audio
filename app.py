from flask import Flask, request, jsonify
import logging
import yt_dlp

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            raise ValueError("URL is required")
        
        # Use yt-dlp to process the URL
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
        
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
