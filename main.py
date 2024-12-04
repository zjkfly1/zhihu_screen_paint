import os
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

import screen
import configparser

from utils import print_current_time

# 创建配置解析器对象
config = configparser.ConfigParser()

# 读取配置文件
config.read("config.ini")

# 获取 host 配置，若为空则使用默认 localhost
host = config.get("host", "local", fallback="http://localhost:8000")
app = Flask(__name__)

# 设置图片所在目录
IMAGE_FOLDER = "images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)


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

        print_current_time(1)

        # 下载图片
        answer_id = screen.Capture_screenshot(image_url)
        # 返回保存的本地路径
        return jsonify({"local_path": f"{host}/images/{answer_id}.png"}), 200

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

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
