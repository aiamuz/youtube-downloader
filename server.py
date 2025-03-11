from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"error": "Missing video URL!"}), 400

    try:
        # اجرای yt-dlp برای دریافت لینک MP4 با بالاترین کیفیت
        command = ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]", "-g", video_url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        download_urls = result.stdout.strip().split("\n")

        if not download_urls:
            return jsonify({"error": "No direct download link found!"}), 404

        return jsonify({
            "message": "Download link generated successfully",
            "videoUrl": video_url,
            "downloadUrl": download_urls[0]  # لینک مستقیم MP4
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to fetch video info", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
