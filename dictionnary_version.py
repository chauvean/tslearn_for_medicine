import pandas as pd
import itertools
from time import time
import datetime
import operator
import collections


class Date_prec:
    def __init__(self, df):
        self.content = []
        self.source = []
        self.target = []
        self.date_from = df.at[df.first_valid_index(), 'datefrom']
        self.date_to = df.at[df.first_valid_index(), 'dateto']
        for a, b in zip(df['Source'], df['Target']):
            self.content.append([a, b])
            self.source.append(a)
            self.target.append(b)
        self.tuples = None

    def set_nb_tuples(self, nb_combi):
        self.tuples = [[[], []] for _ in range(nb_combi)]


class Sequence:
    def __init__(self, date1, date2, content=[]):
        self.patdid = -1
        self.datefrom = date1
        self.dateto = date2
        self.content = content


def get_infos(df, column):
    l = []
    for date in df[column]:
        if date not in l:
            l.append(date)
    return l


def get_column(df, column, value):
    return df[df[column] == value]


def filter_df_by_date(df):
    date_df_list = []
    for date in get_infos(df, 'datefrom'):
        df2 = df[df['datefrom'] == date]
        date_df_list.append(df2[['datefrom', 'dateto', 'Source', 'Target']])
    return date_df_list


def n_sized_precedence(df, n):
    dfs_bydate_list = filter_df_by_date(df)
    class_list = []
    for df in dfs_bydate_list:
        class_list.append(Date_prec(df))
        pass
    for date_class in class_list:
        list_of_tuples = list(itertools.combinations(date_class.content, n))
        date_class.set_nb_tuples(len(list_of_tuples))
        for tuple_index, tuple in enumerate(list_of_tuples):
            for i in range(n):
                date_class.tuples[tuple_index][0].append(tuple[i][0])
                date_class.tuples[tuple_index][1].append(tuple[i][1])
    return class_list


def fill_dic(class_list):
    dic = dict()
    for seq_class in class_list:
        if seq_class.date_from in dic.keys():
            dic[seq_class.date_from].append(seq_class.tuples)
        else:
            dic[seq_class.date_from] = seq_class.tuples
    return dic


def date_to_str(date):
    y, m, d = date.year, date.month, date.day
    if len(str(m)) == 1:
        return ("-").join([str(y), '0' + str(m), str(d)])
    else:
        return ("-").join([str(y), str(m), str(d)])





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


def frequences(list):
    dic = dict()
    for element in list:
        if element not in dic.keys():
            dic[element] = 1
        else:
            dic[element] += 1
    sorted_x = sorted(dic.items(), key=operator.itemgetter(1))
    sorted_dict = collections.OrderedDict(sorted_x)
    return sorted_dict


#  longest_sequence = max(dic.keys(), key=(lambda k: dic[k]))

def sequences_content(sequences_list):
    for sequence in sequences_list:
        print(sequence.content)
    print(len(sequences_list))
def filter_excel_by_column(excel_file, column):
    df = pd.read_excel(excel_file)
    frames = [get_column(df, column, value) for value in get_infos(df, column)]
    return frames

def main():
    # n sequences ok, separation ok, not together, if smaller sequences before
    # t1 = time()
    # # # #TODO dates should of type date (not string as dealt with in the excel files (to allow the date+1, an ordering).
    #l = get_infos(pd.read_excel('bio_precede_full3.xlsx'), 'datefrom')
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
    pat_frames = filter_excel_by_column('test.xlsx', 'trajID')
    pat_sequences = []
    for frame in pat_frames:
        t1=time()
        l = get_infos(frame, 'delta_T0')
        #pat_sequences.append(find_seq_chained_lists(l[0], l[-1], fill_dic(n_sized_precedence(frame, 1))))
        t2=time()
        print(t2-t1)
    # # print(fill_dic(n_sized_precedence('test.xlsx', 1)))
    # # print(fill_dic(n_sized_precedence('bio_precede_full3.xlsx', 3 )))
    # str_date1 = "2017-03-09"
    # year, month, day = str_date1.split("-")
    # date1 = datetime.datetime(int(year), int(month), int(day))
    print("test passed")


main()
