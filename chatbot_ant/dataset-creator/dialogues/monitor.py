'''
Watch Files Processing Progress
'''

import os
import sys
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir))

import time
from config import CONFIG

def watch_dialogues_files_number():
    '''
    Print tsv files number in real time.
    '''
    while True:
        files = os.listdir(CONFIG['data']['output'])
        tsvfiles_len = 0
        for dirname in files:
            for file in os.listdir(CONFIG['data']['output'] + os.sep + dirname):
                if file.endswith(".tsv"):
                    tsvfiles_len += 1
        print tsvfiles_len
        time.sleep(10)

if __name__ == "__main__":
    watch_dialogues_files_number()
