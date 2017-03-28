# coding: utf-8
from math import sqrt
import jieba.analyse
import pymysql

def cut_word(content):
    '''
    [(u'\u65b9\u5e84', 2.4582479479)
    (u'\u82b3\u57ce\u56ed', 1.19547675029)
    (u'\u53ef\u6708\u4ed8', 1.19547675029)
    (u'\u4e00\u533a', 1.04666904475)
    (u'\u5355\u95f4', 1.02371160058)
    (u'\u51fa\u79df', 0.832472854883)
    (u'\u5730\u94c1', 0.8200234078590001)
    (u'\u4e2d\u4ecb', 0.7891864466530001)
    (u'\u9644\u8fd1', 0.516934129144)]
    '''
    tags = jieba.analyse.extract_tags(content, withWeight=True, topK=20)
    return tags


def merge_tag(tag1=None, tag2=None):

    v1 = []
    v2 = []
    tag_dict1 = {i[0]: i[1] for i in tag1}
    tag_dict2 = {i[0]: i[1] for i in tag2}
    merged_tag = set(list(tag_dict1.keys())+list(tag_dict2.keys()))
    for i in merged_tag:
        if i in tag_dict1:
            v1.append(tag_dict1[i])
        else:
            v1.append(0)

        if i in tag_dict2:
            v2.append(tag_dict2[i])
        else:
            v2.append(0)
    return v1, v2


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
    questions_simis = []
    input_con = input("请输入您的问题: ")
    tag1 = cut_word(input_con)
    print(tag1)
    sql = "select question from `data1`.corpus"
    cursor.execute(sql)
    data_set = cursor.fetchall()
    for item in data_set:
        tag2 = cut_word(item[0])
        v1, v2 = merge_tag(tag1, tag2)
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
    print(main())
