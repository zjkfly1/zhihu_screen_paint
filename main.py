from flask import Flask, jsonify, request

import screen
app = Flask(__name__)


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
        screen.Capture_screenshot(image_url)
        # 返回保存的本地路径
        return jsonify({"local_path": ""}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
