import cx_Oracle
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE

print(f"Connecting as {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_SERVICE}")

DSN = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)

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
    return pool.acquire()

def release_connection(conn):
    pool.release(conn)

def close_pool():
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
