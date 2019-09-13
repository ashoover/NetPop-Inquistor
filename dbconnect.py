import pymysql.cursors
import gc

def connection():
    conn = pymysql.connect( host = "localhost",
                            port = 3307,
                            user = "root",
                            passwd = "password",
                            db = "netpop")

    c = conn.cursor()

    return c, conn

    