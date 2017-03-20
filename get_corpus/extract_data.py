import pymysql

databases = ['shortdata2','shortdata2.1']

for i in databases:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='{}'.format(i), charset='utf8')
    cursor = conn.cursor()

    sql = "select question,answer from `{}`.short_corpus".format(i)
    cursor.execute(sql)
    data = cursor.fetchall()

    with open("all_corpus.txt","a",encoding="utf8") as fp:
        for i in data:
            fp.writelines(str(list(i))+"\n")


    cursor.close()
        
    conn.close()

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='data1', charset='utf8')
cursor = conn.cursor()

sql = "select label,question, answer from `data1`.corpus"
cursor.execute(sql)
data = cursor.fetchall()

with open("all_corpus.txt","a",encoding="utf8") as fp:
    for i in data:
        fp.writelines(str(list(i))+"\n")


cursor.close()
    
conn.close()