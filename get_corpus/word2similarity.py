# coding: utf-8
from math import sqrt
import jieba
import pymysql
import gensim



def cut_word(content):
    tags = jieba.cut(content, cut_all=False)
    return tags

def buildWordVector(text, size):
    count = 0
    vec = [0 for i in range(size) ]
    for word in text:
        try:
            vec += imdb_w2v[word]
            count += 1.
        except KeyError:
            continue
    if count != 0:
        vec /= count
    return vec



def dot_product(v1, v2):
   return sum(a * b for a, b in zip(v1, v2))


def magnitude(vector):
    dot = dot_product(vector, vector)
    return sqrt(dot)


def similarity(v1, v2):
    '''计算余弦相似度
    '''
    return dot_product(v1, v2) / (magnitude(v1) * magnitude(v2) + .00000000001)


def main():
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='data1', charset='utf8')
    cursor = conn.cursor()
    size = 100
    questions_simis = []
    input_con = input("请输入您的问题: ")
    tag1 = cut_word(input_con)
    v1 = buildWordVector(tag1,size)
    sql = "select question from `data1`.corpus"
    cursor.execute(sql)
    data_set = cursor.fetchall()
    for item in data_set:
        tag2 = cut_word(item[0])
        v2 = buildWordVector(tag2,size)
        questions_simis.append(similarity(v1, v2))
    index_simi = list(enumerate(questions_simis))
    simi_max = max(questions_simis)
    for index,simi in index_simi:
        if simi == simi_max:
            return_question = data_set[index]
            print(return_question)
    sql1 = "select answer from `data1`.corpus where question = '%s'"%return_question
    cursor.execute(sql1)
    answer = cursor.fetchall()[0][0]
    cursor.close()
    conn.close()
    return answer

if __name__ == '__main__':
    imdb_w2v = gensim.models.KeyedVectors.load_word2vec_format('text.vector', binary=False)
    print(main())
