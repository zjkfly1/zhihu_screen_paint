import os

from flask import Flask, jsonify, request, send_from_directory

import screen
app = Flask(__name__)

# 设置图片所在目录
IMAGE_FOLDER = "images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "Hello, World!"


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "This is a sample API response"})


@app.route('/download_image', methods=['POST'])
def download_image():
    try:
        # 获取用户传递的 URL
        data = request.json
        image_url = data.get("url")
        print(image_url)
        if not image_url:
            return jsonify({"error": "No URL provided"}), 400

        # 下载图片
        answer_id = screen.Capture_screenshot(image_url)
        # 返回保存的本地路径
        return jsonify({"local_path": f"http://localhost:8000/images/{answer_id}.png"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    """
    提供访问图片文件的接口
    """
    try:
        return send_from_directory(IMAGE_FOLDER, filename)
    except FileNotFoundError:
        return {"error": "File not found"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
