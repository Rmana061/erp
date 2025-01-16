from flask import Blueprint, request, jsonify
from backend.config.database import get_db_connection
from backend.utils.password_utils import hash_password
import datetime

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer/list', methods=['GET'])
def get_customer_list():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, company_name, contact_name, phone, 
                   email, address, created_at, updated_at 
            FROM customers 
            WHERE status = 'active'
            ORDER BY created_at DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        customers = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # 格式化日期並調整欄位名稱
        for customer in customers:
            if customer['created_at']:
                customer['created_at'] = customer['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if customer['updated_at']:
                customer['updated_at'] = customer['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            # 將 contact_name 映射為 contact_person 以匹配前端
            if 'contact_name' in customer:
                customer['contact_person'] = customer['contact_name']
                del customer['contact_name']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "data": customers
        })
    except Exception as e:
        print(f"Error in get_customer_list: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@customer_bp.route('/customer/add', methods=['POST'])
def add_customer():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查必要欄位
        required_fields = ['username', 'password', 'company_name', 'contact_person', 
                         'phone', 'email', 'address']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "status": "error",
                    "message": f"缺少必要欄位: {field}"
                }), 400
        
        # 檢查用戶名是否已存在
        cursor.execute("""
            SELECT id FROM customers 
            WHERE username = %s AND status = 'active'
        """, (data['username'],))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "用戶名已存在"
            }), 400
        
        # 檢查信箱是否已存在
        cursor.execute("""
            SELECT id FROM customers 
            WHERE email = %s AND status = 'active'
        """, (data['email'],))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "信箱已存在"
            }), 400
        
        # 密碼加密
        hashed_password = hash_password(data['password'])
        
        # 插入新客戶
        cursor.execute("""
            INSERT INTO customers (
                username, password, company_name, contact_name, 
                phone, email, address, line_account, viewable_products, remark,
                status, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                'active', NOW(), NOW()
            ) RETURNING id
        """, (
            data['username'], hashed_password, data['company_name'],
            data['contact_person'], data['phone'], data['email'],
            data['address'], data.get('line_account', ''),
            data.get('viewable_products', ''), data.get('remark', '')
        ))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "客戶新增成功",
            "id": new_id
        })
        
    except Exception as e:
        print(f"Error in add_customer: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@customer_bp.route('/customer/update', methods=['PUT'])
def update_customer():
    try:
        data = request.json
        if 'id' not in data:
            return jsonify({
                "status": "error",
                "message": "缺少客戶ID"
            }), 400
            
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查客戶是否存在
        cursor.execute("""
            SELECT id FROM customers 
            WHERE id = %s AND status = 'active'
        """, (data['id'],))
        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "客戶不存在"
            }), 404
        
        # 檢查用戶名是否重複
        if 'username' in data:
            cursor.execute("""
                SELECT id FROM customers 
                WHERE username = %s AND id != %s AND status = 'active'
            """, (data['username'], data['id']))
            if cursor.fetchone():
                return jsonify({
                    "status": "error",
                    "message": "用戶名已存在"
                }), 400
        
        # 檢查信箱是否重複
        if 'email' in data:
            cursor.execute("""
                SELECT id FROM customers 
                WHERE email = %s AND id != %s AND status = 'active'
            """, (data['email'], data['id']))
            if cursor.fetchone():
                return jsonify({
                    "status": "error",
                    "message": "信箱已存在"
                }), 400
        
        # 構建更新語句
        update_fields = []
        update_values = []
        
        field_mapping = {
            'username': 'username',
            'company_name': 'company_name',
            'contact_person': 'contact_name',
            'phone': 'phone',
            'email': 'email',
            'address': 'address'
        }
        
        for key, field in field_mapping.items():
            if key in data and data[key] is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(data[key])
        
        # 如果有密碼更新
        if 'password' in data and data['password']:
            update_fields.append("password = %s")
            update_values.append(hash_password(data['password']))
        
        if not update_fields:
            return jsonify({
                "status": "error",
                "message": "沒有提供要更新的欄位"
            }), 400
        
        # 添加更新時間
        update_fields.append("updated_at = NOW()")
        
        # 執行更新
        update_values.append(data['id'])
        update_query = f"""
            UPDATE customers 
            SET {', '.join(update_fields)}
            WHERE id = %s AND status = 'active'
        """
        
        cursor.execute(update_query, tuple(update_values))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "客戶資料更新成功"
        })
        
    except Exception as e:
        print(f"Error in update_customer: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@customer_bp.route('/customer/delete', methods=['DELETE'])
def delete_customer():
    try:
        data = request.json
        if 'id' not in data:
            return jsonify({
                "status": "error",
                "message": "缺少客戶ID"
            }), 400
            
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查客戶是否存在
        cursor.execute("""
            SELECT id FROM customers 
            WHERE id = %s AND status = 'active'
        """, (data['id'],))
        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "客戶不存在"
            }), 404
        
        # 軟刪除客戶
        cursor.execute("""
            UPDATE customers 
            SET status = 'inactive', updated_at = NOW()
            WHERE id = %s
        """, (data['id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "客戶刪除成功"
        })
        
    except Exception as e:
        print(f"Error in delete_customer: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 