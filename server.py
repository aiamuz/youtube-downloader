import os
from flask import Flask, request, jsonify, send_file
import subprocess
import json

app = Flask(__name__)

SAVE_DIR = "/app/downloads"  # مسیر ذخیره ویدیو
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing video URL!"}), 400

    try:
        # دریافت اطلاعات ویدیو
        command = ["yt-dlp", "--dump-json", "--no-playlist", video_url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)

        # انتخاب بهترین فرمت MP4
        best_format = None
        best_height = 0
        for fmt in video_info["formats"]:
            if fmt.get("ext") == "mp4" and fmt.get("vcodec") != "none" and fmt.get("acodec") != "none":
                height = fmt.get("height", 0)
                if height > best_height:
                    best_height = height
                    best_format = fmt["format_id"]

        if not best_format:
            return jsonify({"error": "No suitable MP4 format with video and audio found!"}), 404

        # دانلود و ذخیره ویدیو در سرور
        filename = f"{video_info['id']}.mp4"
        filepath = os.path.join(SAVE_DIR, filename)
        command = ["yt-dlp", "-f", best_format, "-o", filepath, video_url]
        subprocess.run(command, check=True)

        # تولید لینک قابل دانلود در Railway
        download_url = f"https://youtube-downloader-production-e01b.up.railway.app/files/{filename}"

        return jsonify({
            "message": "Download link generated successfully",
            "videoUrl": video_url,
            "videoDownloadUrl": download_url,
            "resolution": f"{best_height}p",
            "format_id": best_format
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to fetch video info", "details": str(e)}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse video format info!"}), 500

@app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    filepath = os.path.join(SAVE_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found!"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
