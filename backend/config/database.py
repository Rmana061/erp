import psycopg2
from psycopg2 import pool

# 創建全局連接池
connection_pool = pool.SimpleConnectionPool(
    minconn=5,      # 最小連接數
    maxconn=20,     # 最大連接數
    host="127.0.0.1",
    port="5432",
    user="postgres",

    password="1qaz2wsx",
    database="postgres"

)

def get_db_connection():
    try:
        # 從連接池獲取連接
        conn = connection_pool.getconn()
        print("Database connection acquired from pool.")
        return conn

    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def release_db_connection(conn):
    try:
        # 將連接歸還到連接池
        if conn is not None:
            connection_pool.putconn(conn)
            print("Database connection returned to pool.")

    except Exception as e:
        print(f"Error returning connection to pool: {e}") 