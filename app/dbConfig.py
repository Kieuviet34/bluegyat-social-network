# dbConfig.py
import cx_Oracle
from config import Config

# Kết nối đến Oracle sử dụng thông tin từ Config
DB_USER = Config.DB_USER
DB_PASSWORD = Config.DB_PASSWORD
DB_HOST = Config.DB_HOST
DB_PORT = Config.DB_PORT
DB_SERVICE = Config.DB_SERVICE

print(f"Connecting as {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_SERVICE}")

# Tạo DSN string cho cx_Oracle
DSN = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)

# Khởi tạo SessionPool
pool = cx_Oracle.SessionPool(
    user      = DB_USER,
    password  = DB_PASSWORD,
    dsn       = DSN,
    min       = 2,
    max       = 5,
    increment = 1,
    encoding  = "UTF-8"
)
print("SessionPool created.")

def get_connection():
    """Lấy 1 kết nối từ pool"""
    return pool.acquire()


def release_connection(conn):
    """Trả kết nối về pool"""
    pool.release(conn)


def close_pool():
    """Đóng pool khi shutdown"""
    pool.close()

if __name__ == "__main__":
    conn = None
    try:
        conn = get_connection()
        print("Oracle version:", conn.version)
    except Exception as e:
        print("ERROR connecting:", e)
    finally:
        if conn:
            release_connection(conn)
        close_pool()
