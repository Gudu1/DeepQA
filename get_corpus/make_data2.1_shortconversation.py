import jieba
import pymysql

conversations_text = open("short_conversations.txt", 'a')
lineids_text = open("short_lineids.txt", 'a')

database_list = ["2","2.1"]
lineid = 0 
for i in database_list:
    conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='shortdata{}'.format(i),charset='utf8')
    cursor = conn.cursor()
    sql = "select question, answer from `shortdata{}`.conversations".format(i)
    cursor.execute(sql)
    chat_pairs =cursor.fetchall()
    for items in chat_pairs: 
        lineids = []
        for m in items:
            content_list = jieba.cut(m, cut_all=False)
            content = " ".join(content_list)
            lines_write_in = str(lineid) + " +++$+++ " + content + "\n"
            lineids_text.write(lines_write_in)
            lineids.append(lineid)
            lineid = lineid + 1
        conversations_text.write("con"+" +++$+++ "+str(lineids)+"\n")
    cursor.close()
    conn.close()

conversations_text.close()
lineids_text.close()
