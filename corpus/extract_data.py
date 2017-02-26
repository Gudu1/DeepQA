import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='data1', charset='utf8')
cursor = conn.cursor()

sql = "select * from data1.corpus"
cursor.execute(sql)
data = cursor.fetchall()

with open("data1.txt","w",encoding="utf8") as fp:
    for i in data:
        fp.writelines(str(list(i))+"\n")


cursor.close()
	
conn.close()