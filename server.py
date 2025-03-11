from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing video URL!"}), 400

    try:
        # اجرای yt-dlp برای دریافت لینک MP4 نهایی با بهترین کیفیت
        command = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "--merge-output-format", "mp4",
            "-g",
            video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        download_url = result.stdout.strip()

        if not download_url:
            return jsonify({"error": "No direct MP4 link found!"}), 404

        return jsonify({
            "message": "Download link generated successfully",
            "videoUrl": video_url,
            "videoDownloadUrl": download_url  # لینک مستقیم MP4 یک‌پارچه
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to fetch video info", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
