from backend.config.database import get_db_connection

def check_logs_table():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 檢查日誌表是否存在
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'logs'
                )
            """)
            table_exists = cursor.fetchone()[0]
            print(f"日誌表是否存在: {table_exists}")
            
            if table_exists:
                # 檢查日誌表中的記錄數量
                cursor.execute("SELECT COUNT(*) FROM logs")
                count = cursor.fetchone()[0]
                print(f"日誌表中的記錄數量: {count}")
                
                if count > 0:
                    # 獲取最新的 5 條日誌記錄
                    cursor.execute("""
                        SELECT id, table_name, operation_type, record_id, 
                               performed_by, user_type, created_at
                        FROM logs
                        ORDER BY created_at DESC
                        LIMIT 5
                    """)
                    logs = cursor.fetchall()
                    print("\n最新的 5 條日誌記錄:")
                    for log in logs:
                        print(f"ID: {log[0]}, 表: {log[1]}, 操作: {log[2]}, 記錄ID: {log[3]}, 執行者: {log[4]} ({log[5]}), 時間: {log[6]}")
                
                # 檢查 get_logs 方法中使用的表和列是否存在
                print("\n檢查關聯表:")
                
                # 檢查 administrators 表
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'administrators')")
                print(f"administrators 表是否存在: {cursor.fetchone()[0]}")
                
                # 檢查 customers 表
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'customers')")
                print(f"customers 表是否存在: {cursor.fetchone()[0]}")
                
                # 檢查 orders 表
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders')")
                print(f"orders 表是否存在: {cursor.fetchone()[0]}")
                
                # 檢查 administrators 表中的 admin_name 列
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'administrators' AND column_name = 'admin_name')")
                print(f"administrators.admin_name 列是否存在: {cursor.fetchone()[0]}")
                
                # 檢查 customers 表中的 company_name 列
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'customers' AND column_name = 'company_name')")
                print(f"customers.company_name 列是否存在: {cursor.fetchone()[0]}")
                
                # 檢查 orders 表中的 order_number 列
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'orders' AND column_name = 'order_number')")
                print(f"orders.order_number 列是否存在: {cursor.fetchone()[0]}")
    
    except Exception as e:
        print(f"檢查日誌表時出錯: {str(e)}")

if __name__ == "__main__":
    check_logs_table() 