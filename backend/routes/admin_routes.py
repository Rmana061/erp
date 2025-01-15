from flask import Blueprint, request, jsonify
from backend.config.database import get_db_connection
from backend.utils.password_utils import hash_password
import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/list', methods=['GET'])
def get_admin_list():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, admin_account, admin_name, staff_no,
                   permission_level_id, status, created_at, updated_at 
            FROM administrators 
            WHERE status = 'active'
            ORDER BY created_at DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        admins = []
        for row in cursor.fetchall():
            admin_dict = dict(zip(columns, row))
            # 格式化日期
            if admin_dict.get('created_at'):
                admin_dict['created_at'] = admin_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if admin_dict.get('updated_at'):
                admin_dict['updated_at'] = admin_dict['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            admins.append(admin_dict)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "data": admins
        })
    except Exception as e:
        print(f"Error in get_admin_list: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": f"獲取管理員列表失敗: {str(e)}"
        }), 500

@admin_bp.route('/admin/add', methods=['POST'])
def add_admin():
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查必要欄位
        required_fields = ['admin_account', 'admin_password', 'admin_name', 
                         'staff_no', 'permission_level_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "status": "error",
                    "message": f"缺少必要欄位: {field}"
                }), 400
        
        # 檢查帳號是否已存在
        cursor.execute("""
            SELECT id FROM administrators 
            WHERE admin_account = %s AND status = 'active'
        """, (data['admin_account'],))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "管理員帳號已存在"
            }), 400
        
        # 檢查工號是否已存在
        cursor.execute("""
            SELECT id FROM administrators 
            WHERE staff_no = %s AND status = 'active'
        """, (data['staff_no'],))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "工號已存在"
            }), 400
        
        # 密碼加密
        hashed_password = hash_password(data['admin_password'])
        
        # 插入新管理員
        cursor.execute("""
            INSERT INTO administrators (
                admin_account, admin_password, admin_name, staff_no,
                permission_level_id, status, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, 'active', NOW(), NOW()
            ) RETURNING id
        """, (
            data['admin_account'], hashed_password, data['admin_name'],
            data['staff_no'], data['permission_level_id']
        ))
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "管理員新增成功",
            "id": new_id
        })
        
    except Exception as e:
        print(f"Error in add_admin: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@admin_bp.route('/admin/update', methods=['PUT'])
def update_admin():
    try:
        data = request.json
        if 'id' not in data:
            return jsonify({
                "status": "error",
                "message": "缺少管理員ID"
            }), 400
            
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查管理員是否存在
        cursor.execute("""
            SELECT id FROM administrators 
            WHERE id = %s AND status = 'active'
        """, (data['id'],))
        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "管理員不存在"
            }), 404
        
        # 檢查帳號是否重複
        if 'admin_account' in data:
            cursor.execute("""
                SELECT id FROM administrators 
                WHERE admin_account = %s AND id != %s AND status = 'active'
            """, (data['admin_account'], data['id']))
            if cursor.fetchone():
                return jsonify({
                    "status": "error",
                    "message": "管理員帳號已存在"
                }), 400
        
        # 檢查信箱是否重複
        if 'email' in data:
            cursor.execute("""
                SELECT id FROM administrators 
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
            'admin_account': 'admin_account',
            'admin_name': 'admin_name',
            'phone': 'phone',
            'email': 'email'
        }
        
        for key, field in field_mapping.items():
            if key in data and data[key] is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(data[key])
        
        # 如果有密碼更新
        if 'admin_password' in data and data['admin_password']:
            update_fields.append("admin_password = %s")
            update_values.append(hash_password(data['admin_password']))
        
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
            UPDATE administrators 
            SET {', '.join(update_fields)}
            WHERE id = %s AND status = 'active'
        """
        
        cursor.execute(update_query, tuple(update_values))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "管理員資料更新成功"
        })
        
    except Exception as e:
        print(f"Error in update_admin: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@admin_bp.route('/admin/delete', methods=['DELETE'])
def delete_admin():
    try:
        data = request.json
        if 'id' not in data:
            return jsonify({
                "status": "error",
                "message": "缺少管理員ID"
            }), 400
            
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 檢查管理員是否存在
        cursor.execute("""
            SELECT id FROM administrators 
            WHERE id = %s AND status = 'active'
        """, (data['id'],))
        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "管理員不存在"
            }), 404
        
        # 軟刪除管理員
        cursor.execute("""
            UPDATE administrators 
            SET status = 'inactive', updated_at = NOW()
            WHERE id = %s
        """, (data['id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "管理員刪除成功"
        })
        
    except Exception as e:
        print(f"Error in delete_admin: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 