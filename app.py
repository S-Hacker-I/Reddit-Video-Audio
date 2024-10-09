from flask import Flask, request, jsonify, send_file, Response, stream_with_context, abort
from flask_cors import CORS
import yt_dlp
import os
import concurrent.futures
import mimetypes

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_file('index.html')

def download_task(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            # Playlist
            video = info['entries'][0]
        else:
            # Single video
            video = info
        
        filename = ydl.prepare_filename(video)
        ydl.download([url])
    return filename

@app.route('/download', methods=['POST'])
def download_video():
    url = request.json['url']
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    
    return jsonify({"filename": os.path.basename(filename), "type": "video"})

@app.route('/download_audio', methods=['POST'])
def download_audio():
    url = request.json['url']
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
    
    return jsonify({"filename": os.path.basename(filename), "type": "audio"})

def process_download(url, ydl_opts, content_type):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(download_task, url, ydl_opts)
            filename = future.result(timeout=300)  # 5 minutes timeout
        
        return jsonify({
            'status': 'success',
            'message': f'{content_type} downloaded successfully',
            'filename': os.path.basename(filename)
        })
    except concurrent.futures.TimeoutError:
        return jsonify({
            'status': 'error',
            'message': f"Download timed out. The {content_type.lower()} might be too large or the server is busy."
        }), 408
    except yt_dlp.utils.DownloadError as e:
        return jsonify({
            'status': 'error',
            'message': f"Download error: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/media/<path:filename>')
def serve_media(filename):
    file_path = os.path.join('downloads', filename)
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    mime_type = 'video/mp4' if filename.endswith('.mp4') else 'audio/mpeg'
    
    return send_file(file_path, 
                     mimetype=mime_type, 
                     as_attachment=True, 
                     download_name=filename)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True, port=65000)
