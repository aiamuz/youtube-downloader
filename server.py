from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing video URL!"}), 400

    try:
        # گرفتن لیست فرمت‌های موجود
        command = [
            "yt-dlp",
            "--list-formats",  # لیست فرمت‌ها رو نشون بده
            "--no-playlist",
            video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        formats_output = result.stdout

        # پیدا کردن بهترین فرمت MP4
        best_format = None
        for line in formats_output.splitlines():
            if "mp4" in line and "video" in line:  # فقط فرمت‌های ویدیویی MP4
                best_format = line.split()[0]  # کد فرمت (مثل 137 برای 1080p)
                break  # اولین MP4 رو می‌گیریم (معمولاً بهترینه)

        if not best_format:
            return jsonify({"error": "No MP4 format found!"}), 404

        # گرفتن لینک مستقیم برای بهترین فرمت
        command = [
            "yt-dlp",
            "-f", f"{best_format}+bestaudio/best",  # بهترین ویدیو + صدا
            "--merge-output-format", "mp4",
            "--no-playlist",
            "--get-url",
            video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        video_download_url = result.stdout.strip()

        if not video_download_url:
            return jsonify({"error": "No direct MP4 link found!"}), 404

        return jsonify({
            "message": "Download link generated successfully",
            "videoUrl": video_url,
            "videoDownloadUrl": video_download_url
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to fetch video info", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
