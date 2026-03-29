import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=3,       # only 3 connections allowed
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

@contextmanager
def get_db():
    print(f"trying to borrow a connection...")
    conn = connection_pool.getconn()
    print(f"got connection: {id(conn)}")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        connection_pool.putconn(conn)
        print(f"returned connection: {id(conn)}")



import threading
from database import get_db

def simulate_request(request_id):
    print(f"request {request_id} — trying to borrow connection...")
    with get_db() as conn:
        print(f"request {request_id} — got connection {id(conn)}")
        import time
        time.sleep(3)      # simulate slow query, hold connection open
        print(f"request {request_id} — done, releasing connection")

threads = []
for i in range(4):         # 4 simultaneous requests, pool only has 3
    t = threading.Thread(target=simulate_request, args=(i,))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()