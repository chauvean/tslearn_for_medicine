import pandas as pd
import itertools
from time import time
import datetime
import operator
import collections
import threading
import openpyxl
from tslearn.generators import random_walks
from tslearn.metrics import cdist_dtw
from clustering import *
import numpy as np
from time import time
from matplotlib import pyplot as plt


class Date_prec:
    def __init__(self, serie=None, df=None):
        self.content = []
        self.source = []
        self.target = []
        if df is not None:
            self.date_from = df.at[df.first_valid_index(), 'datefrom']
            self.date_to = df.at[df.first_valid_index(), 'dateto']
            self.delta_T0 = df.at[df.first_valid_index(), 'delta_T0']
            for source, target, deltat0 in zip(df['Source'], df['Target'], df['delta_T0']):
                self.content.append([source, target])
                self.source.append(source)
                self.target.append(target)
                self.delta_T0 = deltat0
                pass
        if serie is not None:
            self.delta_T0 = 0  # TODO how to get the deltat0 ?
            pass
        self.tuples = None

    def set_nb_tuples(self, nb_combi):
        self.tuples = [[[], []] for _ in range(nb_combi)]


class date_coin:
    def __init__(self, serie=None, df=None):
        if serie is not None:
            self.delta_T0 = serie['delta_T0']
        if df is not None:
            self.delta_T0 = df.at['delta_T0', 0]


class Sequence:
    def __init__(self, date1, date2, content=[]):
        self.patdid = -1
        self.datefrom = date1
        self.dateto = date2
        self.content = content


def get_infos(buff, column, distinct=True):
    l = []
    if type(buff) == 'list':
        for ser in buff:
            pass
            # if ser.values[0] not in l:
            #     l.append(ser.values[0])
    else:
        if distinct:
            for date in buff[column]:
                if date not in l:
                    l.append(date)
        else:
            for date in buff[column]:
                l.append(date)
    return l


def get_column(df, column, value):
    return df[df[column] == value]


def filter_df_by_date(df, col_name):
    df_list = []
    for date in get_infos(df, col_name):
        df_list.append(df[df[col_name] == date])
    return df_list


def n_sized_coincidence(df):
    """
    :return: dictionnary where key is a pattern ( ex: (HGB_L -> BLA_N )
    and values are all the possible dates and pat_did's in the samples
    """
    dic = dict()
    for pat_info_row in df.iterrows():
        if (pat_info_row[1]['Source'], pat_info_row[1]['Target']) in dic.keys():
            dic[(pat_info_row[1]['Source'], pat_info_row[1]['Target'])].append([pat_info_row[1]['date'],
                                                                                pat_info_row[1]['delta_T0'],
                                                                                pat_info_row[1]['trajID']]
                                                                               )
        else:
            dic[(pat_info_row[1]['Source'], pat_info_row[1]['Target'])] = [[pat_info_row[1]['date'],
                                                                            pat_info_row[1]['delta_T0'],
                                                                            pat_info_row[1]['trajID']]]
        pass
    return dic


def fill_dic(class_list, arg):
    dic = dict()
    for seq_class in class_list:
        if arg == 'delta_T0':
            if seq_class.delta_T0 in dic.keys():
                dic[seq_class.delta_T0].append(seq_class.tuples)
            else:
                dic[seq_class.delta_T0] = seq_class.tuples
        if arg == 'source-target':
            if seq_class.sourcetarget in dic.keys():
                dic[seq_class.sourcetarget].append(seq_class.tuples)
            else:
                dic[seq_class.delta_T0] = seq_class.tuples
    return dic


# def n_sized_precedence(df, n, col_name):
#     if col_name == 'delta_T0':
#         dfs_list = filter_df_by_date(df, col_name)
#     if col_name == 'source-target':
#         pass
#     class_list = []
#     for df in dfs_list:
#         class_list.append(Date_prec(None, df))
#     for date_class in class_list:
#         if n == 1:
#             list_of_tuples = date_class.content
#         else:
#             list_of_tuples = list(itertools.combinations(date_class.content, n))
#         date_class.set_nb_tuples(len(list_of_tuples))
#         for tuple_index, tuple in enumerate(list_of_tuples):
#             for i in range(n):
#                 date_class.tuples[tuple_index][0].append(tuple[i][0])
#                 date_class.tuples[tuple_index][1].append(tuple[i][1])
#     return class_list


def date_to_str(date):
    y, m, d = date.year, date.month, date.day
    if len(str(m)) == 1:
        return ("-").join([str(y), '0' + str(m), str(d)])
    else:
        return ("-").join([str(y), str(m), str(d)])


def find_seq_by_deltat0(str_t1, str_t2, dic):
    """
    works if delta_t0   are no holes in the indexes. ( 0,1,2,3,4 is ok 0,2,3,4 isn't)
    I check the next delta_T0, range 1 then 2 then 3. But delta_T0 sequences will have holes after clustering.
    :param str_t1:
    :param str_t2:
    :param dic:
    :return:
    """
    seq_list = []
    t1 = int(str_t1)
    t2 = int(str_t2)
    for seq_index, seq in enumerate(dic[t1]):
        seq_list.append(Sequence(t1, t2, [seq[0][0], seq[1][0]]))
    t = t1
    smaller_sized_seqs = []
    while t < t2:
        new_seqs = []
        for seq in seq_list:
            if date_to_str(t + 1) in dic.keys():
                for pair in dic[date_to_str(t + 1)]:
                    if pair[0][0] == seq.content[-1]:
                        new_seqs.append(Sequence(seq.datefrom, seq.dateto, seq.content + [pair[1][0]]))
        seq_list = new_seqs
        t += 1
    for el in smaller_sized_seqs:
        seq_list.append(el)
    return seq_list


def find_seq_chained_lists(str_date1, str_date2, dic):
    year, month, day = str_date1.split("-")
    date1 = datetime.datetime(int(year), int(month), int(day))
    year, month, day = str_date2.split("-")
    date2 = datetime.datetime(int(year), int(month), int(day))
    seq_list = []
    for seq_index, seq in enumerate(dic[str_date1]):
        seq_list.append(Sequence(date1, date2, [seq[0][0], seq[1][0]]))
    date = date1
    smaller_sized_seqs = []
    while date < date2:
        new_seqs = []
        for seq in seq_list:
            if date_to_str(date + datetime.timedelta(days=1)) in dic.keys():
                for pair in dic[date_to_str(date + datetime.timedelta(days=1))]:
                    if pair[0][0] == seq.content[-1]:
                        new_seqs.append(Sequence(seq.datefrom, seq.dateto, seq.content + [pair[1][0]]))
        seq_list = new_seqs
        date += datetime.timedelta(days=1)
    for el in smaller_sized_seqs:
        seq_list.append(el)
    return seq_list


def frequences(dict):
    return [[key, len(dict[key])] for key in dict.keys]


def filter_excel_by_column(excel_file, column):
    df = pd.read_excel(excel_file)
    frames = [get_column(df, column, value) for value in get_infos(df, column)]
    return frames


def main():
    t0 = time()
    # t1 = time()
    # # # #TODO dates should of type date (not string as dealt with in the excel files (to allow the date+1, an ordering).
    # l = get_infos(pd.read_excel('test.xlsx'), 'datefrom')
    # l = get_infos(pd.read_excel('bio_precede_full3.xlsx'), 'datefrom')
    # l.sort()
    # t2 = time()
    # print(t2 - t1)
    # l2 = find_seq_chained_lists(l[0], l[-1], fill_dic(n_sized_precedence('bio_precede_full3.xlsx', 1)))
    # t3 = time()
    # print(t3 - t2)
    # sequences_content(l2)
    # t4 = time()
    # print(t4 - t3)
    # l2 = ['A', 'B', 'B', 'A', 'A', 'C']
    # print(frequences(l2))
    # pat_frames = filter_excel_by_column('test.xlsx', 'trajID')
    # pat_sequences = []
    # for frame in pat_frames:
    #     t1=time()
    #     l = get_infos(frame, 'delta_T0')
    #     #pat_sequences.append(find_seq_chained_lists(l[0], l[-1], fill_dic(n_sized_precedence(frame, 1))))
    #     t2=time()
    #     print(t2-t1)
    # # print(fill_dic(n_sized_precedence('test.xlsx', 1)))
    # # print(fill_dic (n_sized_precedence('bio_precede_full3.xlsx', 3 )))
    # str_date1 = "2017-03-09"
    # year, month, day = str_date1.split("-")
    # date1 = datetime.datetime(int(year), int(month), int(day))
    # df = pd.read_excel('test.xlsx')
    data = [['hey', 1, 2, 3, 5, 4, 5, 5, 5]]
    c = pd.DataFrame(data)
    tf = time()
    print("test passed")


if __name__ == 'main':
    main()
