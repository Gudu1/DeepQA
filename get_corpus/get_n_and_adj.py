#import jieba.posseg as pseg
import pymysql
import jieba.analyse

conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='123456',db='data1',charset='utf8')
cursor = conn.cursor()

words = input("请输入您的问题: ")
tags = jieba.analyse.extract_tags(words)
add_str = ''
for i in tags:
    if i != "怎么" and i !="做":
        add_str = add_str + "msg.question like '%%{}%%' and ".format(i)

add_str = add_str.rstrip(' and ')
sql = 'select answer from data1.corpus msg where ' + add_str 
#print(sql)

cursor.execute(sql)
answers = cursor.fetchall()[0][0]
print(answers)