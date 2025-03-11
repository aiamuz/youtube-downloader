from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing video URL!"}), 400

    try:
        # اجرای yt-dlp برای دریافت لینک مستقیم MP4 با بالاترین کیفیت
       command = [
    "yt-dlp",
    "-f", "(bv*[ext=mp4][height<=1080]/bv*[ext=mp4]/b[ext=mp4]) + (ba[ext=m4a]/ba/b)",  # ترکیب ویدیو و صدا
    "--merge-output-format", "mp4",  # اجبار ترکیب فرمت به MP4
    "--no-playlist",
    "--print", "url",  # جایگزین --get-url برای نسخه‌های جدید
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
