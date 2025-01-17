from flask import Blueprint, request, jsonify, send_from_directory
from backend.config.database import get_db_connection
from backend.utils.file_handlers import (
    create_product_folder, 
    allowed_image_file, 
    allowed_doc_file, 
    UPLOAD_FOLDER
)
from werkzeug.utils import secure_filename
import os

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
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

@product_bp.route('/products/<int:product_id>', methods=['GET'])
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
        
        for key in ['created_at', 'updated_at']:
            if key in product and product[key]:
                product[key] = product[key].isoformat() if hasattr(product[key], 'isoformat') else str(product[key])
        
        cursor.close()
        conn.close()
        return jsonify(product)
    except Exception as e:
        print(f"Error in get_product: {str(e)}")
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products', methods=['POST'])
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
        
        required_fields = ['name', 'description', 'min_order_qty', 'max_order_qty', 'product_unit']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        try:
            min_qty = int(data.get('min_order_qty'))
            max_qty = int(data.get('max_order_qty'))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity values'}), 400
            
        sql = """
            INSERT INTO products (
                name, description, image_url, dm_url,
                min_order_qty, max_order_qty, product_unit, shipping_time,
                special_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        params = (
            data.get('name'),
            data.get('description'),
            data.get('image_url'),
            data.get('dm_url'),
            min_qty,
            max_qty,
            data.get('product_unit'),
            data.get('shipping_time'),
            data.get('special_date', False)
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

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.json
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
            
        required_fields = ['name', 'description', 'min_order_qty', 'max_order_qty', 'product_unit']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
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
            data.get('special_date', False),
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

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
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

@product_bp.route('/upload/image', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files or 'productName' not in request.form:
            return jsonify({'error': 'Missing file or product name'}), 400
            
        file = request.files['file']
        product_name = request.form['productName']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_image_file(file.filename):
            file_ext = os.path.splitext(file.filename)[1]
            new_filename = secure_filename(product_name) + file_ext
            
            product_folder = create_product_folder(product_name)
            filepath = os.path.join(product_folder, new_filename)
            
            file.save(filepath)
            
            relative_path = os.path.join('uploads', secure_filename(product_name), new_filename)
            return jsonify({
                'message': 'File uploaded successfully',
                'url': f'/{relative_path.replace(os.sep, "/")}'
            })
            
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@product_bp.route('/upload/document', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files or 'productName' not in request.form:
            return jsonify({'error': 'Missing file or product name'}), 400
            
        file = request.files['file']
        product_name = request.form['productName']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_doc_file(file.filename):
            file_ext = os.path.splitext(file.filename)[1]
            new_filename = secure_filename(product_name) + file_ext
            
            product_folder = create_product_folder(product_name)
            filepath = os.path.join(product_folder, new_filename)
            
            file.save(filepath)
            
            relative_path = os.path.join('uploads', secure_filename(product_name), new_filename)
            return jsonify({
                'message': 'File uploaded successfully',
                'url': f'/{relative_path.replace(os.sep, "/")}'
            })
            
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@product_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@product_bp.route('/products/viewable', methods=['GET'])
def get_viewable_products():
    try:
        product_ids = request.args.get('ids', '')
        if not product_ids:
            return jsonify({
                "status": "success",
                "data": []
            })

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        
        # 将逗号分隔的ID字符串转换为列表
        id_list = product_ids.split(',')
        
        # 构建 IN 查询的占位符
        placeholders = ','.join(['%s'] * len(id_list))
        
        # 查询产品信息，包括所有需要的字段
        cursor.execute(f"""
            SELECT id, name, description, min_order_qty, max_order_qty, 
                   product_unit as unit, status
            FROM products 
            WHERE id IN ({placeholders})
            AND status = 'active'
            ORDER BY name
        """, id_list)
        
        columns = [desc[0] for desc in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "data": products
        })

    except Exception as e:
        print(f"Error in get_viewable_products: {str(e)}")
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 