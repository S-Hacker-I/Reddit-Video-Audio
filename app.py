from flask import Flask, request, send_file, jsonify
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
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'noplaylist': True,
    }

    try:
        # Download the video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
            video_file = video_filename.replace('.webm', '.mp4')  # Ensure mp4 format
            
            # Send the file back to the client
            return send_file(video_file, as_attachment=True, attachment_filename='video.mp4')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Use the default port or Render's port
    app.run(debug=True, host='0.0.0.0', port=port)
