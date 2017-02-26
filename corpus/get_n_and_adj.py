import jieba.posseg as pseg

words = input("请输入您的问题")

for word, flag in pseg.cut(words):
    if "n" in flag:
        print("%s,%s"%(word,flag))
    elif "a" in flag:
        print("%s,%s"%(word,flag))
    elif "v" in flag:
        print("%s,%s"%(word,flag))

