from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
from io import BytesIO

app = Flask(__name__)

# Define the download route
@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400

        # Options for yt-dlp to download TikTok video
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloaded_video.%(ext)s',
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(video_url)
            video_filename = ydl.prepare_filename(result)

        # Stream the file back to the client
        with open(video_filename, 'rb') as video_file:
            video_data = BytesIO(video_file.read())

        os.remove(video_filename)  # Clean up the file after streaming

        # Send the video file to the client
        return send_file(
            video_data,
            as_attachment=True,
            download_name='tiktok_video.mp4',
            mimetype='video/mp4'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
