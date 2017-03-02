import jieba

conversations_text = open("conversations.txt", 'a')
lineids_text = open("lineids.txt", 'a')
database_num = ["2","2.1"]
lineid = 0 
for i in database_num:
	with open("shortdata{}_shortcorpus.txt".format(i),'r',encoding="utf8") as fp:
		items = fp.readlines()
		for i in items:
			spliters = [x.lstrip("'[").rstrip("']\n") for x in i.split(", ")]
			question = spliters[1]
			print("question"+question)
			answers = spliters[2]
			split_answer = [j.lstrip(r"\\r\\t\\u3000\\u3000").rstrip("r\\").replace("\\xa0\\xa0",'').replace("xa0",'') for  j in answers.split(r"\n")[1:]]
			while "" in split_answer:
				split_answer.remove("")
			split_answer_again1 = [n.split("。")[0] for n in split_answer]
			split_answer_again2= [n.split("？")[0].strip() for n in split_answer_again1]
			lineids = []
			for m in split_answer_again2:
				content_list = jieba.cut(m, cut_all=False)
				content = " ".join(content_list)
				lines_write_in = str(lineid) + " +++$+++ " + content + "\n"
				lineids_text.write(lines_write_in)
				lineids.append(lineid)
				lineid = lineid + 1
			conversations_text.write("con"+" +++$+++ "+str(lineids)+"\n")
    			
 
conversations_text.close()
lineids_text.close()
