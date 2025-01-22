import os
import sys

# 將專案根目錄添加到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request
from flask_cors import CORS
from backend.routes.product_routes import product_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.customer_routes import customer_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.order_routes import order_bp

app = Flask(__name__)

# Session 配置
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = True  # 使用 HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # 允许跨站点请求
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # session 过期时间设为 30 分钟

# CORS 配置
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "https://f06f-111-249-201-90.ngrok-free.app"
        ],
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# 设置响应头
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:5173", "https://f06f-111-249-201-90.ngrok-free.app"]:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.headers['Vary'] = 'Origin'
    return response

# 註冊藍圖
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)