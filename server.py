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
        # گرفتن اطلاعات فرمت‌ها با --dump-json
        command = [
            "yt-dlp",
            "--dump-json",  # اطلاعات رو به‌صورت JSON بده
            "--no-playlist",
            video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)

        # پیدا کردن بهترین فرمت MP4 که ویدیو و صدا داره
        best_format = None
        best_height = 0
        for format in video_info["formats"]:
            if (format.get("ext") == "mp4" and 
                format.get("vcodec") != "none" and  # مطمئن می‌شیم ویدیو داره
                format.get("acodec") != "none"):    # مطمئن می‌شیم صدا داره
                height = format.get("height", 0)
                if height > best_height:
                    best_height = height
                    best_format = format["format_id"]

        if not best_format:
            return jsonify({"error": "No suitable MP4 format with video and audio found!"}), 404

        # گرفتن لینک مستقیم برای بهترین فرمت
        command = [
            "yt-dlp",
            "-f", best_format,  # فقط بهترین فرمت رو بگیر
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
            "videoDownloadUrl": video_download_url,
            "resolution": f"{best_height}p"  # رزولوشن رو هم برگردونیم برای چک کردن
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to fetch video info", "details": str(e)}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse video format info!"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
