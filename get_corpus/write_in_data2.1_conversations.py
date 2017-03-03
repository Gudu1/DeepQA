import pymysql
import jieba


conn = pymysql.connect(host = '127.0.0.1',port=3306,user='root',passwd='123456',db = 'shortdata2.1',charset='utf8')
cursor = conn.cursor()
with open("shortdata2.1_shortcorpus.txt",'r',encoding="utf8") as fp:
	items = fp.readlines()
	id = 0
	for i in items:
		spliters = [x.lstrip("'[").rstrip("']\n") for x in i.split(", ")]
		question = spliters[1]
		print("question"+question)
		answers = spliters[2]
		split_answer = [j.lstrip(r"\\r\\t\\u3000\\u3000").rstrip("r\\").replace("\\xa0\\xa0",'').replace("xa0",'') for  j in answers.split(r"\n")[1:]]
		while "" in split_answer:
			split_answer.remove("")
		split_answer_again1 = [n.split("。")[0] for n in split_answer]
		split_answer_again2= [n.split("?")[0] for n in split_answer_again1]
		split_answer_again3= [n.split("!")[0] for n in split_answer_again2]
		
		for m in split_answer_again3:
			sql = "INSERT IGNORE INTO `shortdata2.1`.conversations VALUES(%s,%s,%s)"
			cursor.execute(sql,(id,question,m))
			conn.commit()
			id = id + 1
cursor.close()
conn.close()