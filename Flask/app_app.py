from flask import Flask

# 创建 Flask 应用程序对象
app = Flask(__name__)

# 定义路由
@app.route('/')
def index():
    return 'Hello, world! This is my Flask app.'

# 启动应用程序
if __name__ == '__main__':
    # 生产环境中应使用 Gunicorn 或其他 WSGI 服务器启动应用程序
    # 但为了演示目的，我们在开发环境中使用 Flask 自带的开发服务器
    app.run(debug=True)