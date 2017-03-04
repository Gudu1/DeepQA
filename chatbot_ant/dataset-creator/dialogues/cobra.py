# coding:utf8
'''
Preprocessing Data with data_1
'''

import os
import sys
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir))
import time
import shutil
import MySQLdb
from config import CONFIG
from utils import database
from utils import log
from utils import segmenter
from utils import translate
import pickle
import pandas as pd
from collections import OrderedDict

logger = log.getLogger(__file__)

import resource
#resource.setrlimit(resource.RLIMIT_NOFILE, (1000, -1))

# Convert results from SQL Cusor to list
handle_sql_results_for_ids = lambda sql_exec_results: [
    str(list(x)[0]) for x in list(sql_exec_results)]


def save_dict(obj, name):
    with open(CONFIG['data']['pickle'] + os.sep + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_dict(name):
    with open(CONFIG['data']['pickle'] + os.sep + name + '.pkl', 'rb') as f:
        return pickle.load(f)


class Chin(object):
    '''
    Select Data with prepare SQL
    '''

    def __init__(self,conn,lineId):
        self.conn = conn
        self.lineId = lineId

    def get_all_user_ids_by_country(self, country):
        '''
        Get distinct user ids by country
        '''
        ids = []
        try:
            cursor = self.conn.cursor()
            sql = "SELECT DISTINCT id FROM data_1.game_user where country=%d" % country
            cursor.execute(sql)
            ids = handle_sql_results_for_ids(cursor.fetchall())
        except Exception as e:
            logger.error("get_all_user_ids_by_country" + str(e))
        finally:
            cursor.close()
        return ids

    def get_chatting_pairs_by_country(self, country):
        '''
        生成以toUserId为key,以一个toUserId对应的所有userIds(是一个list)的字典
        '''
        try:
            chatting_pairs = {}
            cursor = self.conn.cursor()
            user_ids = self.get_all_user_ids_by_country(country)
            for user_id in user_ids:
                print 'process ', user_id
                sql = "SELECT DISTINCT userId FROM data_1.game_msg where toUserId=%s" % user_id
                cursor.execute(sql)
                contacts = handle_sql_results_for_ids(cursor.fetchall())
                chatting_pairs[user_id] = contacts
                print 'get contacts', contacts
            logger.debug("Chatting Pairs Length: %d" % len(chatting_pairs))
        except Exception as e:
            logger.error("get_chatting_pairs_by_country " + str(e))
        finally:
            cursor.close()
        return chatting_pairs

    def check_repeated_data(self, country):
        try:
            print "++====="
            rechatting_pairs = {}
            rechatting_pairs = self.get_chatting_pairs_by_country(country)
            userids = [userid for userid in rechatting_pairs.keys()]
            for contacts in rechatting_pairs.values():
                for value in contacts:
                    if value in userids:
                        contacts.remove(value)
        except Exception as e:
            logger.error("检查重复数据失败:" + str(e))
        finally:
            logger.info("已经运行check_repeated_data函数")
        return rechatting_pairs

    def dump_chatting_pairs_by_country(self, country):
        save_dict(self.check_repeated_data(
            country), 'chatting_pairs_by_country_%d' % country)

    def retrieve_chatting_pairs_by_country(self, country):
        '''
        First, try to load data from disk, if not exist, 
        compute the data and save it into disk.
        Sometimes, you may want to refresh the data, just 
        run 'rm -rf ../pickle/*.pkl'
        '''
        file_path = CONFIG['data']['pickle'] + os.sep + \
            ('chatting_pairs_by_country_%d' % country)

        if not os.path.exists(file_path + '.pkl'):
            self.dump_chatting_pairs_by_country(country)

        return load_dict('chatting_pairs_by_country_%d' % country)

    def process_chat_history_by_ids(self, user1, user2):
        '''
        Process the dialogues between user1 and user2
        '''
        cursor = self.conn.cursor()
        sql = """SELECT timeline,userId,toUserId,id,REPLACE(REPLACE(msg, '\n', ''), '\r', '') as msg
                            FROM data_1.game_msg t where t.msg != '' 
                            and (t.toUserId=%s and t.userId=%s
                               or t.toUserId = %s and t.userId=%s) 
                            and (t.msg like '%%name%%' or t.msg like '%%名字%%' or t.msg like '%%home%%'  
                               or t.msg like '%%家%%' or t.msg like '%%from%%' or t.msg like '%%来自%%'  
                               or t.msg like '%%old%%' or t.msg like '%%年龄%%' or t.msg like '%%like%%' 
                               or t.msg like '%%love%%' or t.msg like '%%favorite%%' or t.msg like '%%喜欢%%' 
                               or t.msg like '%%grade%%' or t.msg like '%%年级%%' or t.msg like '%%hobby%%' 
                               or t.msg like '%%特长%%' or t.msg like '%%我叫%%' or t.msg like '%%movie%%' 
                               or t.msg like '%%sport%%' or t.msg like '%%live%%' or t.msg like '%%book%%' 
                               or t.msg like '%%ball%%' or t.msg like '%%interest%%' or t.msg like '%%food%%') 
                            ORDER BY t.timeline ASC;
                   """ % (user1, user2, user2, user1)
        
        cursor.execute(sql)
        chat_records = cursor.fetchall()
        cursor.close()
        lineIds = [] # 利用process_chat_history_by_ids得到lineid的list
        record_file_lines = []
        dialog_user_number = len(
            set([chat_record[1] for chat_record in chat_records]))
        if dialog_user_number == 2:
            '''
            If the dialogue are done with two people, not say to oneself.
            '''
            for every_chat_record in chat_records:
                if "我送你一件装备" not in every_chat_record[4].encode('utf8'):
                    userId = str(every_chat_record[1])
                    toUserId = str(every_chat_record[2])
                    msgId = str(every_chat_record[3])
                    msg = every_chat_record[4].encode('utf8')
                    msg = segmenter.process_sentence(msg)
                    cont_strbuf = str(self.lineId) + " +++$+++ " + userId + " +++$+++ " \
                    +  toUserId + " +++$+++ " + msgId + " +++$+++ " + translate.main(msg) + '\n'
                    logger.debug('pipe>>' + cont_strbuf)
                    record_file_lines.append(cont_strbuf)
                    lineIds.append(self.lineId)
                    self.lineId += 1
            
        if len(record_file_lines) > 1:
            '''
            Only save files that have at least one conversations.
            '''
            print "record_file_lines %s" %record_file_lines
            record_txt.writelines(record_file_lines)
            lines_strbuf = user2 + " +++$+++ " \
                + user1 + " +++$+++ " + str(lineIds) + "\n"  # user2是userId,user2是toUserId
            lineids_txt.write(lines_strbuf)    
            return True
        return False

    def generate_dialogues_in_turn(self, country=0):
        '''
        查询msg字段不为空的记录
        '''
        try:
            dialogues_index = {}
            chatting_pairs = self.retrieve_chatting_pairs_by_country(country)
            for user_id, contacts in chatting_pairs.items():
                dialogues_index_userid = []
                compute_index_list = lambda x, y: dialogues_index_userid.append(
                    y) if x == True else None

                [compute_index_list(self.process_chat_history_by_ids(user_id, value), value)
                    for value in contacts
                    if (value != user_id) and (int(value) not in CONFIG['rule']['blacklist'])]
                if len(dialogues_index_userid) > 0:
                    dialogues_index[user_id] = dialogues_index_userid
                    print 'Generate dialogues', 'done', user_id, dialogues_index[user_id]

            '''
            Save the dialogues indexes into disk.
            '''
            logger.info("save dialogues_index dict into disk.")
            save_dict(dialogues_index, 'dialogues_by_country_%d' % country)
        except Exception as e:
            logger.error("提取所有记录失败:" + str(e))
            print e
        finally:
            logger.info("generate_dialogues_by_country_id is done.")


def prepare_dir():
    data_path = CONFIG["data"]["output3"]
    if os.path.exists(data_path):
        logger.info('Delete files ' + data_path)
        shutil.rmtree(data_path)
        os.makedirs(data_path)
    else:
        os.makedirs(data_path)
    return data_path

if __name__ == "__main__":
    data_path = prepare_dir()
    try:
        
        chat_data_path = data_path
        logger.info('Build chat data in ' + chat_data_path)
        record_file_path = chat_data_path + os.sep + "snap_selfintr_lines.txt"
        lineids_file_path = chat_data_path + os.sep + "snap__selfintr_conversation.txt"
        record_txt = open(record_file_path, 'a')
        lineids_txt = open(lineids_file_path, 'a')

        conn = database.get_mysql_conn()
        cnto = Chin(conn,0)
        cnto.generate_dialogues_in_turn(country=0)
        record_txt.close()
        lineids_txt.close()

        conn.close()


    except Exception as e:
        logger.error("最后出现异常" + str(e))
    finally:
        logger.info('>> Job is done.')
        
