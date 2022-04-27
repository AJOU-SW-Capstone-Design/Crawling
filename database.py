import pymysql
import DB_info

def connect():
    conn = pymysql.connect(host=DB_info.host, port=DB_info.port, user=DB_info.user, password=DB_info.password, db=DB_info.db, charset='utf8')
    return conn

def disconnect(conn):
    conn.close()

def execute(execution, sql):
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    if execution == 'select':
        result = cur.fetchall()
        disconnect(conn)
        return result
    conn.commit()
    disconnect(conn)