import pymysql
import jieba

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='shortdata2', charset='utf8')
cursor = conn.cursor()

# sql = "select * from shortdata2.short_corpus"
# cursor.execute(sql)
# data = cursor.fetchall()   # fetch到的是元组（） 用list直接可以将元组转换为list类型

# with open("shortdata2.txt","w",encoding="utf8") as fp:
#     for i in data:
#         fp.writelines(str(list(i))+"\n")

stop_words = ["一、","二、","三、","四、","五、","六","七、","九、","十、",\
             "1、","2、","3、","4、","5、","6、","7、","8、","9、","10、"]
with open("shortdata2.txt","r",encoding = "utf8") as fp1:
   items =  fp1.readlines()
   id = 1 #从1开始
   for j in items: 
       spliters = [x.lstrip("'[").rstrip("']\n") for x in j.split(", ")] # 去除右侧的内容，可以从右往左依次strip,相应的左侧lstrip是从左往右
       question = spliters[1]
       answers = spliters[2]
       split_answer =[i.lstrip(r" \\r\\t\\u3000\\u3000").rstrip("r\\ ").replace("\\xa0\\xa0","") for i in answers.split(r"\n")[1:]]
       while '' in split_answer:
           split_answer.remove('')
       split_answer = split_answer[1:]
       answer = ""
       for element in split_answer:
           #element_list = jieba.cut(element,cut_all = False)
           #answer = [answer + n for n in element_list if n not in stop_words][0]
           sql1 = "INSERT ignore INTO shortdata2.conversations VALUES(%s,%s,%s)"
           cursor.execute(sql1,(id, question, element))
           conn.commit()
           id = id + 1
cursor.close()
	
conn.close()

#报主键的错的解决方法:id是自动主键，故不用在程序中对id自加或者重建了数据表#