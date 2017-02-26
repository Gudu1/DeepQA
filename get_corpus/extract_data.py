import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='shortdata2.1', charset='utf8')
cursor = conn.cursor()

sql = "select * from `shortdata2.1`.short_corpus"
cursor.execute(sql)
data = cursor.fetchall()

with open("shortdata2.1_shortcorpus.txt","w",encoding="utf8") as fp:
    for i in data:
        fp.writelines(str(list(i))+"\n")


cursor.close()
	
conn.close()