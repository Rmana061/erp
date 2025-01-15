import os
import sys

# 將專案根目錄添加到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from backend.routes.product_routes import product_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.customer_routes import customer_bp
from backend.routes.admin_routes import admin_bp

app = Flask(__name__)

# CORS 設置
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True
    }
})

# 註冊藍圖
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)