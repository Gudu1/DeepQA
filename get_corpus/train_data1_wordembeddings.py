import jieba
import gensim
import os,time

write_in_file = open("cut_data1_corpus.txt","a",encoding="utf8")
with open("data1_corpus.txt","r",encoding="utf8") as fp:
    con = fp.read()
    phrases = jieba.cut(con,cut_all = False)
    stopwords = [line.split("\n")[0] for line in open("StopwordsCN.txt",encoding='utf8')]
    words = [phrase for phrase in phrases if phrase not in stopwords]
    words = " ".join(words)
    write_in_file.write(words+"\n")
write_in_file.close()

t1 = time.time()
model = gensim.models.Word2Vec(gensim.models.word2vec.LineSentence("cut_data1_corpus.txt"),size=100,window = 3, min_count = 3)
t2 = time.time()
usetime = str(t2 - t1)
print(usetime)
print(model.most_similar("茄子"))
if os.path.exists("text.vector"):
        os.remove("text.vector")
model.wv.save_word2vec_format("text.vector",binary = False)
model.init_sims(replace=True)