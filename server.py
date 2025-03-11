from flask import Flask, request, jsonify, send_from_directory
import subprocess
import json
import os
import time

app = Flask(__name__)

# مسیر ذخیره ویدیوها
SAVE_DIR = "/app/downloads"
os.makedirs(SAVE_DIR, exist_ok=True)

# **تابع حذف فایل‌های قدیمی‌تر از 6 ساعت**
def cleanup_old_files():
    now = time.time()
    for filename in os.listdir(SAVE_DIR):
        filepath = os.path.join(SAVE_DIR, filename)
        if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > 6 * 3600:
            os.remove(filepath)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing video URL!"}), 400

    # **پاک‌سازی فایل‌های قدیمی**
    cleanup_old_files()

    try:
        # گرفتن اطلاعات فرمت‌ها با yt-dlp
        command = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)

        # پیدا کردن بهترین فرمت MP4 با ویدیو و صدا
        best_format = None
        best_height = 0
        for format in video_info["formats"]:
            if (format.get("ext") == "mp4" and 
                format.get("vcodec") != "none" and 
                format.get("acodec") != "none"):
                height = format.get("height", 0)
                if height > best_height:
                    best_height = height
                    best_format = format["format_id"]

        if not best_format:
            return jsonify({"error": "No suitable MP4 format with video and audio found!"}), 404

        # دانلود و ذخیره ویدیو
        output_path = os.path.join(SAVE_DIR, "%(id)s.%(ext)s")
        command = [
            "yt-dlp",
            "-f", best_format,
            "--no-playlist",
            "-o", output_path,
            video_url
        ]
        subprocess.run(command, check=True)

        # پیدا کردن نام فایل دانلود شده
        downloaded_files = [f for f in os.listdir(SAVE_DIR) if f.startswith(video_info["id"])]
        if not downloaded_files:
            return jsonify({"error": "Download failed"}), 500

        filename = downloaded_files[0]
        video_download_url = f"https://youtube-downloader-production-e01b.up.railway.app/files/{filename}"

        return jsonify({
            "message": "Download link generated successfully",
            "videoUrl": video_url,
            "videoDownloadUrl": video_download_url,
            "resolution": f"{best_height}p",
            "format_id": best_format
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to fetch video info", "details": str(e)}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse video format info!"}), 500

# **مسیر برای دریافت فایل‌های دانلود شده**
@app.route('/files/<filename>')
def get_file(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
