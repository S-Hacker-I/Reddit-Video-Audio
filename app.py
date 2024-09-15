from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import subprocess
import logging
import time
import tempfile
import threading

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Thread lock to handle concurrent downloads
lock = threading.Lock()

def download_video(url, format):
    options = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(tempfile.gettempdir(), 'temp_video.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.join(tempfile.gettempdir(), 'temp_video.' + info.get('ext', 'mp4'))

def convert_to_mp4(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, output_file]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("Error during video conversion") from e

def generate_unique_filename(base_name, extension):
    counter = 1
    while os.path.exists(f"{base_name}_{counter}.{extension}"):
        counter += 1
    return f"{base_name}_{counter}.{extension}"

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format = request.form.get('format', 'mp4')
    
    if not url:
        logging.error('URL is required')
        return jsonify({'error': 'URL is required'}), 400

    # Unique filename for each download request
    download_filename = generate_unique_filename(tempfile.gettempdir() + '/temp_video', 'mp4')

    try:
        logging.info(f'Starting download for URL: {url} with format: {format}')
        
        # Download video
        with lock:  # Ensure that downloads do not overlap
            video_file = download_video(url, format)
        
        # Convert if needed
        if format != 'mp4':
            output_file = download_filename
            convert_to_mp4(video_file, output_file)
            video_file = output_file
        
        # Ensure the file is not being used by another process
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            try:
                with open(video_file, 'rb'):
                    break
            except IOError:
                time.sleep(1)
                attempt += 1
        else:
            logging.error(f'File {video_file} is still in use or not found')
            return jsonify({'error': 'File is not ready'}), 500
        
        if not os.path.exists(video_file):
            logging.error(f'File {video_file} not found')
            return jsonify({'error': 'File not found'}), 500
        
        # Determine the correct mimetype
        mime_type = 'video/mp4' if format == 'mp4' else 'audio/mpeg'
        
        logging.info(f'Sending file {video_file}')
        response = send_file(video_file, as_attachment=True, download_name='video.' + format, mimetype=mime_type)
        
        # Cleanup the temporary file
        try:
            os.remove(video_file)
        except Exception as e:
            logging.error(f'Error removing file {video_file}: {str(e)}')
        
        return response
    
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=True)
