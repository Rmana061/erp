from flask import Blueprint, request, jsonify
from backend.config.database import get_db_connection
from backend.utils.password_utils import verify_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, admin_account, admin_password 
            FROM administrators 
            WHERE admin_account = %s 
            AND status = 'active'
        """, (data['username'],))
        
        user = cursor.fetchone()
        if user is None:
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        if not verify_password(data['password'], user[2]):
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        cursor.close()
        conn.close()
        
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

@auth_bp.route('/customer-login', methods=['POST'])
def customer_login():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, password 
            FROM customers 
            WHERE username = %s 
            AND status = 'active'
        """, (data['username'],))
        
        customer = cursor.fetchone()
        if customer is None:
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        if not verify_password(data['password'], customer[2]):
            return jsonify({"error": "帳號或密碼錯誤"}), 401
            
        cursor.close()
        conn.close()
        
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