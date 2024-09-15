from flask import Flask, request, send_file
import yt_dlp
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return {"error": "URL is required"}, 400

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
    
    video_file = 'video.mp4'
    return send_file(video_file, as_attachment=True, attachment_filename='video.mp4')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
