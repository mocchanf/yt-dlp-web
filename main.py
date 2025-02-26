from flask import Flask, request, jsonify, send_file
import subprocess
import os
import uuid

app = Flask(__name__)

# ダウンロードフォルダを作成
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "yt-dlp Web API is running! Use /download to download videos."

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "URL is required"}), 400

    # 一意のファイル名を作成
    video_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.mp4")

    try:
        # yt-dlp を実行して動画をダウンロード
        command = [
            "yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]", "--merge-output-format", "mp4",
            "-o", output_path, video_url
        ]
        subprocess.run(command, check=True)

        return jsonify({"download_url": f"/file/{video_id}.mp4"})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Download failed", "details": str(e)}), 500

@app.route('/file/<filename>', methods=['GET'])
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
