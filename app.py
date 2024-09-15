from flask import Flask, request, jsonify, send_file
import yt_dlp
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Define the options for yt-dlp
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download best video and audio
            'outtmpl': 'downloads/video.mp4',     # Save as video.mp4 in the downloads folder
            'quiet': True,
            'noplaylist': True,
            'merge_output_format': 'mp4'
        }

        # Ensure the downloads directory exists
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Send the file back to the client
        return send_file('downloads/video.mp4', as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
