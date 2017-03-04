# coding:utf8
'''
Generate meta data
testfiles.csv trainfiles.csv  valfiles.csv
'''
from __future__ import division
import os
import sys

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir))
import random
import pickle
import shutil
import csv
from utils import log
from config import CONFIG

logger = log.getLogger(__file__)

def get_file_dir_element():
    file_dir_elements = []
    dialogue_path = CONFIG['data']['output']
    touserid_folders = os.listdir(dialogue_path)
    for touserid_folder in touserid_folders:
        # os.listdir()括号中要求是一个路径
        for contact in os.listdir(os.path.join(dialogue_path, touserid_folder)):
            file_dir_elements.append([contact, touserid_folder])
    return file_dir_elements


def write_in_csvfile(filename, write_in_data):
    meta_path = CONFIG["data"]["meta"]
    file_path = meta_path + os.sep + filename
    with open(file_path, 'wb') as csvfile:
        for element in write_in_data:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(element)


def prepare_dir():
    meta_path = CONFIG["data"]["meta"]
    if not os.path.exists(meta_path):
        os.makedirs(meta_path)
    else:
        shutil.rmtree(meta_path)
        os.makedirs(meta_path)  # 删除原来的meta文件,再建一个空的meta文件夹
    return meta_path


def generate_meta_data():
    '''
    Generate meta data
    '''
    meta_path = prepare_dir()
    file_dir_elements = get_file_dir_element()
    random.shuffle(file_dir_elements)
    file_dir_len = len(file_dir_elements)
    train_len = int(file_dir_len * (5 / 7))
    vali_len = int(file_dir_len * (1 / 7))
    test_len = int(file_dir_len * (1 / 7))

    train_elements = file_dir_elements[0:train_len]
    write_in_csvfile("trainfiles.csv", train_elements)

    validation_elements = file_dir_elements[train_len + 1:train_len + 1 + vali_len]
    write_in_csvfile("valfiles.csv", validation_elements)

    test_elements = file_dir_elements[-test_len:]
    write_in_csvfile("testfiles.csv", test_elements)

    print "训练数据个数是%d" % train_len
    print "训练数据个数是%d" % len(validation_elements)
    print "测试数据个数是%d" % len(test_elements)

if __name__ == "__main__":
    prepare_dir()
    generate_meta_data()

