# coding: utf8
import argparse
import os
import unicodecsv
import random
from six.moves import urllib
import tarfile
import csv
from config import CONFIG

import nltk
from nltk.stem import SnowballStemmer, WordNetLemmatizer

__author__ = 'hain'

"""
Script for generation of train, test and valid datasets from Snaplingo Corpus 1 on 1 dialogs.
Copyright Snaplingo Corporation 2016
LICENSE: Apache License 2.0  URL: ttp://www.apache.org/licenses/LICENSE-2.0
Contact: Rudolf Kadlec (hain@snaplingo.com)
"""

dialog_end_symbol = "__dialog_end__"
end_of_utterance_symbol = "__eou__"
end_of_turn_symbol = "__eot__"


def translate_dialog_to_lists(dialog_filename):
    """
    Translates the dialog to a list of lists of utterances. In the first
    list each item holds subsequent utterances from the same user. The second level
    list holds the individual utterances.
    得到的list中,包含多个list,第一个list里面是同一个user的utterances,其他的(除了最后一个)每一个list
    是另外一个人的每一句话,最后一个list是结束符.
    :param dialog_filename:
    :return:
    """
    dialog_file = open(dialog_filename, 'r')
    dialog_reader = unicodecsv.reader(
        dialog_file, delimiter='\t', quoting=csv.QUOTE_NONE)

    # go through the dialog
    first_turn = True
    dialog = []
    same_user_utterances = []
    # last_user = None
    dialog.append(same_user_utterances)

    for dialog_line in dialog_reader:
        if first_turn:
            last_user = dialog_line[1]
            first_turn = False

        if last_user != dialog_line[1]:
            # user has changed
            same_user_utterances = []
            dialog.append(same_user_utterances)  # 增加一个新的list

        same_user_utterances.append(dialog_line[3])

        last_user = dialog_line[1]

    dialog.append([dialog_end_symbol])

    return dialog


def get_random_utterances_from_corpus(candidate_dialog_paths, rng, utterances_num=9, min_turn=1, max_turn=20):
    """
    modification: 将min_turn由3改为1
    Sample multiple random utterances from the whole corpus.
    :param candidate_dialog_paths:
    :param rng:
    :param utterances_num: number of utterances to generate
    :param min_turn: minimal index of turn that the utterance is selected from
    :return:
    """
    utterances = []
    dialogs_num = len(candidate_dialog_paths)

    for i in xrange(0, utterances_num):
        # sample random dialog
        dialog_path = candidate_dialog_paths[rng.randint(0, dialogs_num - 1)]
        # load the dialog
        dialog = translate_dialog_to_lists(dialog_path)

        # we do not count the last  _dialog_end__ urn
        dialog_len = len(dialog) - 1
        if(dialog_len < min_turn):
            print "Dialog {} was shorter than the minimum required lenght {}".format(dialog_path, dialog_len)
            # exit()
        # sample utterance, exclude the last round that is always "dialog end"
        # 但是我们的语料中存在一个对话窗口中只有一个小朋友说话,此时dialog_len为1,所以max_ix会出现为0的情况
        max_ix = min(max_turn, dialog_len) - 1

        # this code deals with corner cases when dialogs are too short
        if min_turn - 1 == max_ix:
            turn_index = max_ix
        else:
           # if min_turn >  max_ix: #过滤掉只有一个小朋友说话的情况 只有一个小朋友说话时,max_ix长度为0时
              #  continue
            turn_index = rng.randint(min_turn, max_ix)

        utterance = singe_user_utterances_to_string(dialog[turn_index])
        utterances.append(utterance)
    return utterances


def singe_user_utterances_to_string(utterances_list):
    """
    Concatenates multiple user's utterances into a single string.
    :param utterances_list:
    :return:
    """
    return " ".join(map(lambda x: x + " " + end_of_utterance_symbol, utterances_list))


def dialog_turns_to_string(dialog):
    """
    Translates the whole dialog (list of lists) to a string
    :param dialog:
    :return:
    """
    # join utterances
    turns_as_strings = map(singe_user_utterances_to_string, dialog)
    # join turns
    return "".join(map(lambda x: x + " " + end_of_turn_symbol + " ", turns_as_strings))


def create_random_context(dialog, rng, minimum_context_length=2, max_context_length=20):
    """
    Samples random context from a dialog. Contexts are uniformly sampled from the whole dialog.
    :param dialog:
    :param rng:
    :return: context, index of next utterance that follows the context
    """
    # sample dialog context
    # context_turns = rng.randint(minimum_context_length,len(dialog)-1)
    max_len = min(max_context_length, len(dialog)) - 2
    if max_len <= minimum_context_length:
        context_turns = max_len
    else:
        context_turns = rng.randint(minimum_context_length, max_len)

    # create string
    return dialog_turns_to_string(dialog[:context_turns]), context_turns


def create_single_dialog_train_example(context_dialog_path, candidate_dialog_paths, rng, positive_probability,
                                       minimum_context_length=0, max_context_length=20):
    """
    modify minimum_context_length from 2 into 0 to make min_turn 1
    Creates a single example for training set.
    :param context_dialog_path:
    :param candidate_dialog_paths:
    :param rng:
    :param positive_probability:
    :return:
    """

    dialog = translate_dialog_to_lists(context_dialog_path)

    context_str, next_utterance_ix = create_random_context(dialog, rng,
                                                           minimum_context_length=minimum_context_length,
                                                           max_context_length=max_context_length)

    if positive_probability > rng.random():
        # use the next utterance as positive example
        response = singe_user_utterances_to_string(dialog[next_utterance_ix])
        label = 1.0
    else:
        response = get_random_utterances_from_corpus(candidate_dialog_paths, rng, 1,
                                                     min_turn=minimum_context_length + 1,
                                                     max_turn=max_context_length)[0]
        label = 0.0
    return context_str, response, label


def create_single_dialog_test_example(context_dialog_path, candidate_dialog_paths, rng, distractors_num, max_context_length):
    """
    Creates a single example for testing or validation. Each line contains a context, one positive example and N negative examples.
    :param context_dialog_path:
    :param candidate_dialog_paths:
    :param rng:
    :param distractors_num:
    :return: triple (context, positive response, [negative responses])
    """

    dialog = translate_dialog_to_lists(context_dialog_path)

    context_str, next_utterance_ix = create_random_context(
        dialog, rng, max_context_length=max_context_length)

    # use the next utterance as positive example
    positive_response = singe_user_utterances_to_string(
        dialog[next_utterance_ix])

    negative_responses = get_random_utterances_from_corpus(
        candidate_dialog_paths, rng, distractors_num)
    return context_str, positive_response, negative_responses


def create_examples_train(candidate_dialog_paths, rng, positive_probability=0.5, max_context_length=20):
    """
    Creates single training example.
    :param candidate_dialog_paths:
    :param rng:
    :param positive_probability: probability of selecting positive training example
    :return:
    """
    i = 0
    examples = []
    for context_dialog in candidate_dialog_paths:
        if i % 1000 == 0:
            print str(i)
        dialog_path = candidate_dialog_paths[i]
        examples.append(create_single_dialog_train_example(dialog_path, candidate_dialog_paths, rng, positive_probability,
                                                           max_context_length=max_context_length))
        i += 1
    # return map(lambda dialog_path :
    # create_single_dialog_train_example(dialog_path, candidate_dialog_paths,
    # rng, positive_probability), candidate_dialog_paths)


def create_examples(candidate_dialog_paths, examples_num, creator_function):
    """
    Creates a list of training examples from a list of dialogs and function that transforms a dialog to an example.
    :param candidate_dialog_paths:
    :param creator_function:
    :return:
    """
    i = 0
    examples = []
    unique_dialogs_num = len(candidate_dialog_paths)

    while i < examples_num:
        context_dialog = candidate_dialog_paths[i % unique_dialogs_num]
        # counter for tracking progress
        if i % 1000 == 0:
            print str(i)
        i += 1

        examples.append(creator_function(
            context_dialog, candidate_dialog_paths))

    return examples


def convert_csv_with_dialog_paths(csv_file):
    """
    Converts CSV file with comma separated paths to filesystem paths.
    :param csv_file:
    :return:
    """
    def convert_line_to_path(line):
        file, dir = map(lambda x: x.strip(), line.split(","))
        return os.path.join(dir, file)

    return map(convert_line_to_path, csv_file)


def prepare_data_maybe_download(directory):
    """
    Download and unpack dialogs if necessary.
    """
    filename = 'ubuntu_dialogs.tgz'
    url = 'http://cs.mcgill.ca/~jpineau/datasets/ubuntu-corpus-1.0/ubuntu_dialogs.tgz'
    dialogs_path = os.path.join(directory, 'dialogs')

    # test it there are some dialogs in the path
    if not os.path.exists(os.path.join(directory, "10", "1.tst")):
        # dialogs are missing
        archive_path = os.path.join(directory, filename)
        if not os.path.exists(archive_path):
            # archive missing, download it
            print("Downloading %s to %s" % (url, archive_path))
            filepath, _ = urllib.request.urlretrieve(url, archive_path)
            print "Successfully downloaded " + filepath

        # unpack data
        if not os.path.exists(dialogs_path):
            print("Unpacking dialogs ...")
            with tarfile.open(archive_path) as tar:
                tar.extractall(path=directory)
            print("Archive unpacked.")

        return

##########################################################################
# Command line script related code
##########################################################################

if __name__ == '__main__':

    def create_eval_dataset(args, file_list_csv):
        rng = random.Random(args.seed)
        # training dataset
        f = open(os.path.join(CONFIG['data']['meta'], file_list_csv), 'r')
        dialog_paths = map(lambda path: os.path.join(
            CONFIG['data']['output'], path), convert_csv_with_dialog_paths(f))

        data_set = create_examples(dialog_paths,
                                   len(dialog_paths),
                                   lambda context_dialog, candidates: create_single_dialog_test_example(context_dialog, candidates, rng,
                                                                                                        args.n, args.max_context_length))
        # output the dataset
        w = unicodecsv.writer(open(os.path.join(CONFIG['data']['csvfiles'], args.output), 'w'), encoding = 'utf-8')
        # header
        header=["Context", "Ground Truth Utterance"]
        header.extend(map(lambda x: "Distractor_{}".format(x), xrange(args.n)))
        w.writerow(header)

        stemmer= SnowballStemmer("english")
        lemmatizer= WordNetLemmatizer()

        for row in data_set:
            translated_row= [row[0], row[1]]
            translated_row.extend(row[2])

            if args.tokenize:
                nltk.download()
                translated_row= map(nltk.word_tokenize, translated_row)
                if args.stem:
                    translated_row= map(lambda sub: map(
                        stemmer.stem, sub), translated_row)
                if args.lemmatize:
                    translated_row=map(lambda sub: map(
                        lambda tok: lemmatizer.lemmatize(tok, pos='v'), sub), translated_row)

                translated_row=map(lambda x: " ".join(x), translated_row)

            w.writerow(translated_row)
        print("Dataset stored in: {}".format(
            os.path.join(CONFIG['data']['csvfiles'], args.output)))

    def train_cmd(args):

        rng=random.Random(args.seed)
        # training dataset

        f=open(os.path.join(CONFIG['data']['meta'], "trainfiles.csv"), 'r')
        dialog_paths=map(lambda path: os.path.join(
            CONFIG['data']['output'], path), convert_csv_with_dialog_paths(f))

        train_set=create_examples(dialog_paths,
                                    args.examples,
                                    lambda context_dialog, candidates:
                                    create_single_dialog_train_example(context_dialog, candidates, rng,
                                                                       args.p, max_context_length=args.max_context_length))

        stemmer=SnowballStemmer("english")
        lemmatizer=WordNetLemmatizer()

        # output the dataset
        w=unicodecsv.writer(open(os.path.join(
            CONFIG['data']['csvfiles'], args.output), 'w'), encoding = 'utf-8')
        # header
        w.writerow(["Context", "Utterance", "Label"])
        for row in train_set:
            translated_row=row

            if args.tokenize:
                translated_row=[nltk.word_tokenize(row[i]) for i in [0, 1]]

                if args.stem:
                    translated_row=map(lambda sub: map(
                        stemmer.stem, sub), translated_row)
                if args.lemmatize:
                    translated_row= map(lambda sub: map(
                        lambda tok: lemmatizer.lemmatize(tok, pos='v'), sub), translated_row)

                translated_row=map(lambda x: " ".join(x), translated_row)
                translated_row.append(int(float(row[2])))

            w.writerow(translated_row)
        print("Train dataset stored in: {}".format(
            os.path.join(CONFIG['data']['csvfiles'], args.output)))

    def valid_cmd(args):
        create_eval_dataset(args, "valfiles.csv")

    def test_cmd(args):
        create_eval_dataset(args, "testfiles.csv")

    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description = "Script that creates train, valid and test set from 1 on 1 dialogs in Ubuntu Corpus. " +
                                                 "The script downloads 1on1 dialogs from internet and then it randomly samples all the datasets with positive and negative examples.")

    parser.add_argument('--seed', type = int, default = 1234,
                        help='seed for random number generator')

    parser.add_argument('--max_context_length', type=int, default=20,
                        help='maximum number of dialog turns in the context')

    parser.add_argument('-o', '--output', default=None,
                        help='output csv')

    parser.add_argument('-t', '--tokenize', action='store_true',
                        help='tokenize the output')

    parser.add_argument('-l', '--lemmatize', action='store_true',
                        help='lemmatize the output by nltk.stem.WorldNetLemmatizer (applied only when -t flag is present)')

    parser.add_argument('-s', '--stem', action='store_true',
                        help='stem the output by nltk.stem.SnowballStemmer (applied only when -t flag is present)')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_train = subparsers.add_parser('train', help='trainset generator')
    parser_train.add_argument(
        '-p', type=float, default=0.5, help='positive example probability')
    # default值从1000000改为48000
    parser_train.add_argument('-e', '--examples', type=int,
                              default=48000, help='number of examples to generate')
    parser_train.set_defaults(func=train_cmd)

    parser_test = subparsers.add_parser('test', help='testset generator')
    parser_test.add_argument('-n', type=int, default=9,
                             help='number of distractor examples for each context')
    parser_test.set_defaults(func=test_cmd)

    parser_valid = subparsers.add_parser('valid', help='validset generator')
    parser_valid.add_argument(
        '-n', type=int, default=9, help='number of distractor examples for each context')
    parser_valid.set_defaults(func=valid_cmd)

    args = parser.parse_args()

    # download and unpack data if necessary
    # prepare_data_maybe_download(args.data_root)

    # create dataset
    args.func(args)
