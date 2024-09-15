from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import subprocess

app = Flask(__name__)
CORS(app)

def download_video(url, format):
    options = {
        'format': 'bestvideo+bestaudio/best',  # Adjust format settings as needed
        'outtmpl': 'temp_video.%(ext)s',
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return 'temp_video.' + info.get('ext', 'mp4')

def convert_to_mp4(input_file):
    output_file = 'converted_video.mp4'
    command = ['ffmpeg', '-i', input_file, output_file]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception("Error during video conversion") from e
    return output_file

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format = request.form.get('format', 'mp4')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        video_file = download_video(url, format)
        
        if format != 'mp4':
            video_file = convert_to_mp4(video_file)
        
        # Determine the correct mimetype
        mime_type = 'video/mp4' if format == 'mp4' else 'audio/mpeg'
        
        # Ensure file is available and correct
        if not os.path.exists(video_file):
            return jsonify({'error': 'File not found'}), 500
        
        response = send_file(video_file, as_attachment=True, download_name='video.' + format, mimetype=mime_type)
        
        # Cleanup the temporary file
        os.remove(video_file)
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
