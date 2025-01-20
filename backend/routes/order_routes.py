from flask import Blueprint, request, jsonify
from backend.config.database import get_db_connection
from datetime import datetime

order_bp = Blueprint('order', __name__)

@order_bp.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        print("Received order data:", data)
        
        # 验证必填字段
        required_fields = ['order_number', 'customer_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必填欄位: {field}'
                }), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({
                'status': 'error',
                'message': '數據庫連接失敗'
            }), 500

        cursor = conn.cursor()
        
        try:
            # 1. 首先创建主订单
            order_sql = """
                INSERT INTO orders (order_number, customer_id, created_at)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            
            cursor.execute(order_sql, (
                data['order_number'],
                data['customer_id'],
                datetime.now()
            ))
            
            order_id = cursor.fetchone()[0]
            
            # 2. 然后创建订单详情
            details_sql = """
                INSERT INTO order_details (
                    order_id, product_id, product_quantity,
                    product_unit, order_status, shipping_date,
                    remark, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            # 遍历所有产品并创建详情记录
            for product in data['products']:
                cursor.execute(details_sql, (
                    order_id,
                    product['product_id'],
                    product['product_quantity'],
                    product['product_unit'],
                    product['order_status'],
                    product['shipping_date'] if product['shipping_date'] else None,
                    product.get('remark', ''),
                    datetime.now()
                ))
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'message': '訂單創建成功',
                'data': {
                    'order_id': order_id,
                    'order_number': data['order_number']
                }
            }), 201
            
        except Exception as e:
            conn.rollback()
            raise e
        
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        print(f"Error in create_order: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@order_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        customer_id = request.args.get('customer_id')
        if not customer_id:
            return jsonify({
                'status': 'error',
                'message': '缺少客戶ID'
            }), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({
                'status': 'error',
                'message': '數據庫連接失敗'
            }), 500

        cursor = conn.cursor()
        
        # 查询订单和订单详情数据
        sql = """
            SELECT 
                o.id as order_id,
                o.order_number,
                o.customer_id,
                o.created_at as order_created_at,
                od.id as detail_id,
                od.product_id,
                p.name as product_name,
                od.product_quantity,
                od.product_unit,
                od.order_status,
                od.shipping_date,
                od.remark,
                od.created_at as detail_created_at
            FROM orders o
            JOIN order_details od ON o.id = od.order_id
            JOIN products p ON od.product_id = p.id
            WHERE o.customer_id = %s
            ORDER BY o.created_at DESC, od.created_at ASC;
        """
        
        cursor.execute(sql, (customer_id,))
        rows = cursor.fetchall()
        
        # 重组数据结构
        orders = {}
        for row in cursor.fetchall():
            order_id = row['order_id']
            if order_id not in orders:
                orders[order_id] = {
                    'order_id': row['order_id'],
                    'order_number': row['order_number'],
                    'customer_id': row['customer_id'],
                    'created_at': row['order_created_at'],
                    'details': []
                }
            
            orders[order_id]['details'].append({
                'detail_id': row['detail_id'],
                'product_id': row['product_id'],
                'product_name': row['product_name'],
                'product_quantity': row['product_quantity'],
                'product_unit': row['product_unit'],
                'order_status': row['order_status'],
                'shipping_date': row['shipping_date'],
                'remark': row['remark'],
                'created_at': row['detail_created_at']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': list(orders.values())
        })
        
    except Exception as e:
        print(f"Error in get_orders: {str(e)}")
        if 'conn' in locals():
            if 'cursor' in locals():
                cursor.close()
            conn.close()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 