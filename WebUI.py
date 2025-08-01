import os
import subprocess
from flask import Flask, render_template, jsonify, request, send_from_directory
import threading
import toml

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.toml')
MAIN_PATH = os.path.join(BASE_DIR, 'main.py')
CONFIG_UI_PATH = os.path.join(BASE_DIR, 'config_UI', 'config_UI.py')

main_process = None
main_lock = threading.Lock()
main_output_buffer = []

@app.route('/')
def index():
    return send_from_directory('webui', 'index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = toml.load(f)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)})

@app.route('/api/start', methods=['POST'])
def start_main():
    global main_process
    global main_output_buffer
    with main_lock:
        if main_process and main_process.poll() is None:
            return jsonify({'success': False, 'msg': '程序已在运行'})
        main_output_buffer = []
        main_process = subprocess.Popen(['python', MAIN_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        threading.Thread(target=read_main_output, daemon=True).start()
    return jsonify({'success': True})

def read_main_output():
    global main_process, main_output_buffer
    while main_process and main_process.poll() is None:
        line = main_process.stdout.readline()
        if line:
            main_output_buffer.append(line)

@app.route('/api/stop', methods=['POST'])
def stop_main():
    global main_process
    with main_lock:
        if main_process and main_process.poll() is None:
            main_process.terminate()
            main_process = None
            return jsonify({'success': True})
        return jsonify({'success': False, 'msg': '程序未在运行'})

@app.route('/api/output', methods=['GET'])
def get_output():
    global main_output_buffer
    if main_output_buffer:
        output = ''.join(main_output_buffer)
        main_output_buffer.clear()
        return jsonify({'success': True, 'output': output})
    return jsonify({'success': True, 'output': ''})

@app.route('/api/open_config', methods=['POST'])
def open_config():
    # Windows下用powershell新开窗口运行config_UI.py
    # 用powershell的Start-Process强制新窗口运行config_UI.py
    import shutil
    pwsh_path = shutil.which('powershell') or 'powershell'
    subprocess.Popen([
        pwsh_path,
        '-Command',
        f"Start-Process powershell -ArgumentList '-NoExit','python \"{CONFIG_UI_PATH}\"'"
    ], cwd=os.path.dirname(CONFIG_UI_PATH))
    return jsonify({'success': True})

@app.route('/webui/<path:path>')
def send_webui(path):
    return send_from_directory('webui', path)

if __name__ == '__main__':
    import webbrowser
    import time
    webui_dir = os.path.join(BASE_DIR, 'webui')
    if not os.path.exists(webui_dir):
        os.makedirs(webui_dir)
# 前端页面请放在webui/index.html、webui/app.js、webui/style.css中维护
# 只需保证webui目录存在即可
threading.Timer(1, lambda: webbrowser.open('http://127.0.0.1:5010')).start()
app.run(host='127.0.0.1', port=5010, debug=True)
