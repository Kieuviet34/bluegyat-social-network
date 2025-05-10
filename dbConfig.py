import cx_Oracle
try:
    conn = cx_Oracle.connect('kieuviet34/27032004@localhost:1521/orcl')
    print(conn.version)
except cx_Oracle.DatabaseError as e:
    print(e)
