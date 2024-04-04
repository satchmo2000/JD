import os
import hashlib

from flask import Flask, session, request, jsonify, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import signal
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'app_ysk'
CORS(app)

def makeMD5():
    # 生成一个随机字符串
    random_string = os.urandom(16)

    # 创建一个MD5哈希对象
    md5_hash = hashlib.md5()

    # 更新哈希对象，使用随机字符串作为输入
    md5_hash.update(random_string)

    # 获取MD5哈希值的十六进制表示形式
    md5_hex = md5_hash.hexdigest()

    print("Random MD5 hash:", md5_hex)
    
    return md5_hex

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server is None:
        ppid = os.getppid()
        print('shutdown_server is None, then kill the ppid=', ppid)
        os.kill(ppid, signal.SIGTERM)
        return 'Server shutting down by kill process...'
        #raise RuntimeError('Not running with the Werkzeug Server')
    print('ready to shutdown_server.')
    shutdown_server()
    print('return to command line.')
    return 'Server shutting down...'

@app.route('/generate', methods=['POST'])
def generate_text():
    print('request:', request)
    data = request.get_json()
    print('data:', data)
    A = data['A']
    B = data['B']

    # 解码生成的tokens为文本
    generated_text = A + B
    
    outJson = {'code':True, 'err_msg': generated_text}
    
    print('generated_text: ', generated_text, 'return:', outJson)

    return jsonify(outJson)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print('method=', request.method)
    if request.method == 'POST':
        print('Check file', request.files)
        # 检查是否有文件上传
        if 'file' not in request.files:
            print('No file part')
            return jsonify({'code':False, 'err_msg': 'No file part.'})

        file = request.files['file']
        print('Check file is null', file)
        # 如果文件名为空，返回错误
        if file.filename == '':
            print('No selected file')
            return jsonify({'code':False, 'err_msg': 'No selected file.'})

        # 保存文件到指定目录
        print('Secure filename', file.filename)
        filename = secure_filename(file.filename)
        print('upload filename: ', filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('save file: ', os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'code':True, 'count': 1, 'filename': filename, 'err_msg': 'File uploaded and saved.'})

    return jsonify({'code':False, 'err_msg': 'Please use post method.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)