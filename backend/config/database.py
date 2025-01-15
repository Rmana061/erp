import psycopg2

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