import pandas as pd
import itertools
from time import time
import datetime


class DATE_prec:
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

    def gen_tuples(self, n):
        self.tuples = list(itertools.combinations(self.content, n))


def prec_to_dict(prec_info, size):
    dic = dict()
    df = pd.read_excel(prec_info)
    # for val, index in enumerate(zip(df['Source'],df['Target'])):
    #     dic[df.loc[index:index+size, ['Source', 'Target']])] = index
    # return dic


class Sequence:
    def __init__(self, date1, date2):
        self.datefrom = date1
        self.dateto = date2
        self.content = []


def get_dates(df):
    l = []
    for date in df['datefrom']:
        if date not in l:
            l.append(date)
    return l


def filter_df_by_date(excel_file):
    date_df_list = []
    df = pd.read_excel(excel_file)
    for date in get_dates(df):
        df2 = df[df['datefrom'] == date]
        date_df_list.append(df2[['datefrom', 'dateto', 'Source', 'Target']])
    return date_df_list


def n_sized_precedence(prec_file, n):
    dfs_bydate_list = filter_df_by_date(prec_file)
    class_list = []
    for df in dfs_bydate_list:
        class_list.append(DATE_prec(df))
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


# def find_sequences(date1, date2, dic):
#     #init
#     sequence_dict = dict()
#     date = date1
#     for seq_index, seq in enumerate(dic[date]):
#         sequence_dict[seq_index] = []
#
#     while date < date2:
#         for seq in sequence_dict[date]:
#             pass
def date_to_str(date):
    y, m, d = date.year, date.month, date.day
    if len(str(m)) == 1:
        return ("-").join([str(y), '0' + str(m), str(d)])
    else:
        return ("-").join([str(y), str(m), str(d)])


def find_seq_chained_lists(str_date1, str_date2, dic):
    # convert str to date
    year, month, day = str_date1.split("-")
    date1 = datetime.datetime(int(year), int(month), int(day))
    year, month, day = str_date2.split("-")
    date2 = datetime.datetime(int(year), int(month), int(day))
    seq_list = []
    for seq_index, seq in enumerate(dic[str_date1]):
        s = Sequence(date1, date2)
        s.content.append(seq[0][0])
        s.content.append(seq[1][0])
        seq_list.append(s)

    date = date1
    i = 0
    # while date <= date2:
    while date < date2:
        for pair in dic[date_to_str(date + datetime.timedelta(days=1))]:
            nb_possible_sequence = 0
            new_seqs = []
            for seq in seq_list:
                new_seqs = []
                if pair[0][0] == seq.content[-1]:
                    if nb_possible_sequence < 1:
                        seq2=seq
                        seq2.content.append(pair[1][0])
                        nb_possible_sequence += 1
                    else:
                        new_branch_seq = seq
                        new_branch_seq.content.append(pair[1])
                        new_seqs.append(new_branch_seq)
            seq_list += new_seqs
            date += datetime.timedelta(days=1)
            i += 1
    return seq_list


def sequences_content(sequences_list):
    for sequence in sequences_list:
        print(sequence.content)


def main():
    # t1 = time()
    # # #TODO dates should of type date (not string as dealt with in the excel files (to allow the date+1, an ordering).
    l = get_dates(pd.read_excel('test.xlsx'))
    # t2 = time()
    # print(t2 - t1)
    l2 = find_seq_chained_lists(l[0], l[-1], fill_dic(n_sized_precedence('test.xlsx', 1)))
    sequences_content(l2)

    # # print(fill_dic(n_sized_precedence('test.xlsx', 1)))
    # # print(fill_dic(n_sized_precedence('bio_precede_full3.xlsx', 3 )))
    # str_date1 = "2017-03-09"
    # year, month, day = str_date1.split("-")
    # date1 = datetime.datetime(int(year), int(month), int(day))
    # t3 = time()
    # print(t3 - t2)
    print("test passed")


main()
