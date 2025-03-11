import os
import time
import json
import subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

SAVE_DIR = "/app/downloads"  # مسیر ذخیره ویدیوها
os.makedirs(SAVE_DIR, exist_ok=True)
EXPIRATION_TIME = 6 * 60 * 60  # زمان حذف خودکار (6 ساعت)

# تابع حذف فایل‌های قدیمی‌تر از 6 ساعت
def cleanup_old_files():
    now = time.time()
    for filename in os.listdir(SAVE_DIR):
        filepath = os.path.join(SAVE_DIR, filename)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > EXPIRATION_TIME:
                os.remove(filepath)
                print(f"🗑️ Deleted old file: {filename}")

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing video URL!"}), 400

    try:
        # حذف فایل‌های قدیمی قبل از دانلود جدید
        cleanup_old_files()

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

        # ایجاد لینک دانلود صحیح
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

# 🔥 **مسیر جدید برای ارائه فایل‌های دانلود شده**
@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
