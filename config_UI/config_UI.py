import os
import toml
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.toml')

@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        return jsonify({"success": True, "config": config})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/api/config', methods=['POST'])
def save_config():
    try:
        data = request.json.get('config')
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(os.path.dirname(__file__), 'config_UI.html')

@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory(os.path.dirname(__file__), path)

if __name__ == '__main__':
    import webbrowser
    import threading
    def open_browser():
        webbrowser.open('http://127.0.0.1:5008')
    threading.Timer(1, open_browser).start()
    app.run(host='127.0.0.1', port=5008, debug=False, use_reloader=False)
