from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import psycopg2
import bcrypt
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from hash_password import hash_password, verify_password  # 引入加密函數

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

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            user="postgres",
            password="1qaz2wsx",
            database="postgres"
        )
        print("Database connection established.")
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        query = """
            SELECT 
                id, 
                company_name, 
                username, 
                password, 
                line_account, 
                contact_name,
                phone, 
                email, 
                address, 
                viewable_products, 
                remark, 
                created_at, 
                updated_at
            FROM customers;
        """
        cursor.execute(query)
        customers = cursor.fetchall()
        cursor.close()
        conn.close()
        
        customers_list = []
        for customer in customers:
            customers_list.append({
                "id": customer[0],
                "company_name": customer[1],
                "username": customer[2],
                "password": customer[3],
                "line_account": customer[4],
                "contact_name": customer[5],
                "phone": customer[6],
                "email": customer[7],
                "address": customer[8],
                "viewable_products": customer[9],
                "remark": customer[10],
                "created_at": str(customer[11]) if customer[11] else None,
                "updated_at": str(customer[12]) if customer[12] else None
            })
        
        return jsonify(customers_list)
        
    except Exception as e:
        print(f"Database error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, image_url, dm_url, 
                   min_order_qty, max_order_qty, product_unit, 
                   shipping_time, special_date, created_at, updated_at 
            FROM products
            WHERE status = 'active'
        """)
        
        columns = [desc[0] for desc in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify(products)
    except Exception as e:
        print(f"Error in get_products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        # 改為更新 status 為 'inactive'，而不是真正刪除
        cursor.execute("""
            UPDATE products 
            SET status = 'inactive', 
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (product_id,))
            
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': f'Product {product_id} status updated to inactive'})
    except Exception as e:
        print(f"Error in delete_product: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, image_url, dm_url, 
                   min_order_qty, max_order_qty, product_unit, 
                   shipping_time, special_date, created_at, updated_at 
            FROM products 
            WHERE id = %s
        """, (product_id,))
        
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        
        if row is None:
            return jsonify({'error': 'Product not found'}), 404
            
        product = dict(zip(columns, row))
        
        # 處理日期格式，只處理實際的日期時間欄位
        for key in ['created_at', 'updated_at']:
            if key in product and product[key]:
                product[key] = product[key].isoformat() if hasattr(product[key], 'isoformat') else str(product[key])
        
        # shipping_time 是字符串，不需要特殊處理
        
        cursor.close()
        conn.close()
        return jsonify(product)
    except Exception as e:
        print(f"Error in get_product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    conn = None
    cursor = None
    try:
        data = request.json
        print("Received data:", data)
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查必要欄位
        required_fields = ['name', 'description', 'min_order_qty', 'max_order_qty', 'product_unit']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 轉換數字類型
        try:
            min_qty = int(data.get('min_order_qty'))
            max_qty = int(data.get('max_order_qty'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity values'}), 400
            
        # 準備 SQL 語句
        sql = """
            INSERT INTO products (
                name, description, image_url, dm_url,
                min_order_qty, max_order_qty, product_unit, shipping_time,
                special_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        # 準備參數
        params = (
            data.get('name'),
            data.get('description'),
            data.get('image_url'),
            data.get('dm_url'),
            min_qty,
            max_qty,
            data.get('product_unit'),
            data.get('shipping_time'),
            data.get('special_date', False)  # 默认为 False
        )
        
        cursor.execute(sql, params)
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'id': new_id
        }), 201
        
    except Exception as e:
        print(f"Error in create_product: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查產品是否存在
        cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
            
        # 檢查必要欄位
        required_fields = ['name', 'description', 'min_order_qty', 'max_order_qty', 'product_unit']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 更新產品資料
        cursor.execute("""
            UPDATE products 
            SET name = %s,
                description = %s,
                image_url = %s,
                dm_url = %s,
                min_order_qty = %s,
                max_order_qty = %s,
                product_unit = %s,
                shipping_time = %s,
                special_date = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            data.get('name'),
            data.get('description'),
            data.get('image_url'),
            data.get('dm_url'),
            data.get('min_order_qty'),
            data.get('max_order_qty'),
            data.get('product_unit'),
            data.get('shipping_time'),
            data.get('special_date', False),  # 默认为 False
            product_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Product {product_id} updated successfully',
            'id': product_id
        })
        
    except Exception as e:
        print(f"Error in update_product: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({'error': str(e)}), 500

# 修改上傳文件的存儲路徑設置
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # 使用當前工作目錄
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx'}

def create_product_folder(product_name):
    """創建產品文件夾"""
    folder_path = os.path.join(UPLOAD_FOLDER, secure_filename(product_name))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_doc_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOC_EXTENSIONS

@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files or 'productName' not in request.form:
            return jsonify({'error': 'Missing file or product name'}), 400
            
        file = request.files['file']
        product_name = request.form['productName']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_image_file(file.filename):
            # 獲取文件副檔名
            file_ext = os.path.splitext(file.filename)[1]
            # 用產品名稱+副檔名作為新檔名
            new_filename = secure_filename(product_name) + file_ext
            
            # 創建產品文件夾
            product_folder = create_product_folder(product_name)
            
            # 完整的文件路徑
            filepath = os.path.join(product_folder, new_filename)
            
            # 保存文件
            file.save(filepath)
            
            # 返回相對路徑
            relative_path = os.path.join('uploads', secure_filename(product_name), new_filename)
            return jsonify({
                'message': 'File uploaded successfully',
                'url': f'/{relative_path.replace(os.sep, "/")}'
            })
            
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/document', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files or 'productName' not in request.form:
            return jsonify({'error': 'Missing file or product name'}), 400
            
        file = request.files['file']
        product_name = request.form['productName']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_doc_file(file.filename):
            # 獲取文件副檔名
            file_ext = os.path.splitext(file.filename)[1]
            # 用產品名稱+副檔名作為新檔名
            new_filename = secure_filename(product_name) + file_ext
            
            # 創建產品文件夾
            product_folder = create_product_folder(product_name)
            
            # 完整的文件路徑
            filepath = os.path.join(product_folder, new_filename)
            
            # 保存文件
            file.save(filepath)
            
            # 返回相對路徑
            relative_path = os.path.join('uploads', secure_filename(product_name), new_filename)
            return jsonify({
                'message': 'File uploaded successfully',
                'url': f'/{relative_path.replace(os.sep, "/")}'
            })
            
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 添加訪問上傳文件的路由
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers 
            SET status = 'inactive', 
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (customer_id,))
            
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Customer not found'}), 404
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': f'Customer {customer_id} status updated to inactive'})
    except Exception as e:
        print(f"Error in delete_customer: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admins/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE administrators 
            SET status = 'inactive', 
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (admin_id,))
            
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Admin not found'}), 404
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': f'Admin {admin_id} status updated to inactive'})
    except Exception as e:
        print(f"Error in delete_admin: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admins', methods=['POST'])
def create_admin():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查必要欄位
        required_fields = ['admin_account', 'admin_password', 'admin_name', 'staff_no']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 檢查帳號是否已存在
        cursor.execute("SELECT id FROM administrators WHERE admin_account = %s", (data['admin_account'],))
        if cursor.fetchone():
            return jsonify({'error': '已有相同帳號請重新輸入'}), 400
            
        # 檢查工號是否已存在
        cursor.execute("SELECT id FROM administrators WHERE staff_no = %s", (data['staff_no'],))
        if cursor.fetchone():
            return jsonify({'error': 'Staff number already exists'}), 400
        
        # 對密碼進行加密
        hashed_password = hash_password(data['admin_password'])
        
        # 插入新管理員
        cursor.execute("""
            INSERT INTO administrators (
                admin_account, admin_password, admin_name, staff_no,
                permission_level_id, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            data['admin_account'],
            hashed_password,  # 使用加密後的密碼
            data['admin_name'],
            data['staff_no'],
            data.get('permission_level_id', 1),
            data.get('status', 'active')
        ))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({
            'message': 'Administrator created successfully',
            'id': new_id
        }), 201
        
    except Exception as e:
        print(f"Error in create_admin: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 獲取用戶資料，同時檢查 status 是否為 active
        cursor.execute("""
            SELECT id, admin_account, admin_password 
            FROM administrators 
            WHERE admin_account = %s 
            AND status = 'active'
        """, (data['username'],))
        
        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        # 驗證密碼
        if not verify_password(data['password'], user[2]):
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        cursor.close()
        conn.close()
        
        # 登入成功，設置 session
        response = jsonify({
            "message": "Login successful",
            "user_id": user[0]
        })
        
        return response
        
    except Exception as e:
        print(f"Error in login: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/admins', methods=['GET'])
def get_admins():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, admin_account, admin_name, staff_no, permission_level_id, status
            FROM administrators 
            WHERE status = 'active'
            ORDER BY created_at DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        admins = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify(admins)
    except Exception as e:
        print(f"Error in get_admins: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/customer-login', methods=['POST'])
def customer_login():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 獲取客戶資料
        cursor.execute("""
            SELECT id, username, password 
            FROM customers 
            WHERE username = %s 
            AND status = 'active'
        """, (data['username'],))
        
        customer = cursor.fetchone()
        if customer is None:
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        # 驗證密碼
        if not verify_password(data['password'], customer[2]):
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        cursor.close()
        conn.close()
        
        # 登入成功，設置 session
        response = jsonify({
            "message": "Login successful",
            "customer_id": customer[0]
        })
        
        return response
        
    except Exception as e:
        print(f"Error in customer_login: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)