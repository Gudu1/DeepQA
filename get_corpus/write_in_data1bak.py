import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='data1', charset='utf8')
cursor = conn.cursor()
with open("data1.txt","r",encoding = "utf8") as fp1:
   items =  fp1.readlines()
   for j in items:
       spliters = [x.lstrip("'[").rstrip("\n]'").replace("\\xa0","") for x in j.split(", ")] # 去除右侧的内容，可以从右往左依次strip,相应的左侧lstrip是从左往右
       id = spliters[0]
       label = spliters[1]
       question = spliters[2]
       answers = spliters[3]
       sql1 = "INSERT ignore INTO data1.corpus VALUES(%s,%s,%s,%s)"
       cursor.execute(sql1,(id, label, question, answers))
       conn.commit()
cursor.close()
	
conn.close()