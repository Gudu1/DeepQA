import gensim
import time, os, sys
import jieba


if os.path.exists("cut_all_corpus.txt"):
            os.remove("cut_all_corpus.txt")
write_in_file = open("cut_all_corpus.txt","a",encoding="utf8")
with open("all_corpus.txt",encoding="utf8") as fp:

    items =  fp.readlines()
    items1 = items[:16009]
    for j in items1:
        spliters = [x.lstrip("'[").rstrip("']\n") for x in j.split(", '")] # 去除右侧的内容，可以从右往左依次strip,相应的左侧lstrip是从左往右
        item_con = ""
        for m in spliters:
            split_con =[i.lstrip(r" \\r\\t\\u3000\\u3000").rstrip("r\\ ").replace("\\xa0\\xa0","").replace("xa0",'') for i in m.split(r"\n")[1:]]
            while '' in split_con:
                split_con.remove('')
            for con in split_con:
                item_con = item_con + con
        phrases = jieba.cut(item_con,cut_all = False)
        
        stopwords = [line.split("\n")[0] for line in open("StopwordsCN.txt",encoding='utf8')]
        words = [phrase for phrase in phrases if phrase not in stopwords]
        words = " ".join(words)
        write_in_file.write(words+"\n")
    items2 = items[16009:]
    for s_con in items2:
        phrases = jieba.cut(s_con,cut_all = False)
        
        stopwords = [line.split("\n")[0] for line in open("StopwordsCN.txt",encoding='utf8')]
        words = [phrase for phrase in phrases if phrase not in stopwords]
        words = " ".join(words)
        write_in_file.write(words+"\n")
        
write_in_file.close()
# class MySentences(object): 
#     def __init__(self, dirname):
#         self.dirname = dirname
#     def __iter__(self):
#         for line in open(os.path.join(self.dirname,"allcut.txt"),encoding="utf8"):
#             yield line.split()

t1 = time.time()
#sentences = MySentences(r"D:\PYTHON")
model = gensim.models.Word2Vec(gensim.models.word2vec.LineSentence("cut_all_corpus.txt"),size=100,window = 5, min_count = 3)

#model.save()
t2 = time.time()
usetime = str(t2 - t1)
print(usetime)
print(model.most_similar("茄子"))
if os.path.exists("text.vector"):
        os.remove("text.vector")
model.wv.save_word2vec_format("text.vector",binary = False)
model.init_sims(replace=True)