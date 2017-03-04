# coding: utf8
'''
connect to mysql
'''
import os
import sys
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir))

import MySQLdb
from config import CONFIG


def get_mysql_conn():
    '''
    Get a mysql db connection
    '''
    mysql_host = CONFIG["mysql"]["host"]
    mysql_port = int(CONFIG["mysql"]["port"])
    mysql_username = CONFIG["mysql"]["username"]
    mysql_password = CONFIG["mysql"]["password"]
    mysql_db_name = CONFIG["mysql"]["database"]
    return MySQLdb.Connect(host=mysql_host,
                           user=mysql_username,
                           passwd=mysql_password,
                           port=mysql_port,
                           db=mysql_db_name,
                           charset='utf8mb4')


def retrieve_user_records_by_id(id1, id2):
    '''
    Retrive records from database between two users.
    Return mysqlcursor
    https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-fetchone.html
    '''
    CONN = get_mysql_conn()
    cursor = CONN.cursor()
    sql = """SELECT * FROM data_1.game_msg
        where game_msg.userId in (%d, %d)
        and game_msg.toUserId in  (%d, %d);
        """ % (id1, id2, id1, id2)
    # print result
    # print str(cursor.fetchall())
    cursor.execute(sql)
    return cursor

if __name__ == "__main__":
    dataCursor = retrieve_user_records_by_id(2382, 14277)
    for row in dataCursor:
        msg_id = row[0]
        msg_type = row[1]
        msg_userId = row[2]
        msg_toUserId = row[3]
        msg_content = row[4].encode('utf8')
        msg_ext = row[5]
        msg_timeline = row[6]
        if msg_userId != msg_toUserId:
            print (str(msg_timeline) + "  "
                   + str(msg_userId) + "  "
                   + str(msg_toUserId) + "  "
                   + msg_content + "\n")
