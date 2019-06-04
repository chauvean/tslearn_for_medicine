from dict_analysis import *
from clustering import *


def _check_no_empty_cluster(labels, n_clusters):
    for k in range(n_clusters):
        if numpy.sum(labels == k) == 0:
            raise EmptyClusterError
    else:
        return 1


def get_infos_multiple_columns(df, columns):
    """
    same as get_infos when we want values of multiple columns
    :return: l with values of required columns
    """
    l = []
    for column in columns:
        l.append(get_infos(df, column))
    return l


def draw_sil_complexity(df):
    y = []
    c = 0
    array = get_infos(df, 'delta_T0')
    ndarray = [[el] for el in array]
    nb_samples = len(ndarray)
    timeserie = to_time_series_dataset(ndarray)
    for nb_clusters in range(2, nb_samples, 100):
        print(nb_clusters)
        cluster = TimeSeriesKMeans(n_clusters=nb_clusters, verbose=False, max_iter=5, metric="dtw", random_state=0).fit(
            timeserie)
        ta = time()
        silhouette_score(timeserie, cluster.labels_)
        tb = time()
        y.append(tb - ta)
        c += 1
    plt.plot(range(c), y)
    plt.show()


def choose_timelapses(df, treshold=2.0, index=-1):
    """
    Beware, if all the to_be_clustered cells have the same values there will be only one cluster, and an error with silouhettes ccoefficients.
    Problem here, if we maximize this coeff the clusters will be composed of only same delta_t0, so no precedences.
    For each possible nb of clusters, if more than a label, calculate silouhette coeffs, and iterate to find the best coeff.

    For each possible nb of clusters. Uses tslearn library to implement kmeans.
    if more than one label calculate siloihette coeffs. (If only one sil returns an error).
    When new max sil score found. we update the new best cluster.
    :param df:
    :return:
    """
    if index != -1:
        df = df.iloc[:index]
    array = get_infos(df, 'delta_T0')
    ndarray = [[el] for el in array]
    nb_samples = len(ndarray)
    timeserie = to_time_series_dataset(ndarray)
    best_clusterisation = None
    max_sil_score = -2
    # we test all possible nb of clusters
    for nb_clusters in range(2, nb_samples):
        cluster = TimeSeriesKMeans(n_clusters=nb_clusters, verbose=False, max_iter=5, metric="dtw", random_state=0).fit(
            timeserie)
        given_labels = []
        for label in cluster.labels_:
            if label not in given_labels:
                given_labels.append(label)

        if len(given_labels) > 1:  # if all values are the same 1 cluster everytime so silouette error
            ta = time()
            sil = silhouette_score(timeserie, cluster.labels_)
            tb = time()
            # print("sil time : {}".format(tb - ta))
            # print("sil_score for {} clusters is {} ".format(nb_clusters, sil))
            # cluster.labels_.sort()
            # print(cluster.labels_)
            # if some cluster is empty, the silouette score can be optimal ( adding an empty cluster to an optimal set will leave it optimal )
            _check_no_empty_cluster(cluster.labels_, nb_clusters)
            if _check_no_empty_cluster(cluster.labels_, nb_clusters):
                # change the best cluster if the score is better
                if sil > max_sil_score:
                    max_sil_score = sil
                    best_clusterisation = cluster
                    if sil > treshold:
                        return best_clusterisation, max_sil_score
                else:  # score increasing then decrease so when it decreases we can finish without missing better scores
                    return best_clusterisation, max_sil_score
    return 1, 0


def list_serie_to_df(series_list):
    """
    in associate_traj_cluster we use iterrows which return series
    we convert to df as other functions needs df instead of series
    :return: dataframe of the list of series
    """
    df_list = []
    for series in series_list:
        df_for_one_cluster = []
        for serie in series:
            df_for_one_cluster.append(pd.DataFrame([list(serie.values)]))
        df_list.append(pd.concat(df_for_one_cluster))
    return df_list


# def pattern_for_each_cluster_prec(excel_file):
#     df = pd.read_excel(excel_file)
#     best_clustering = choose_timelapses(df)[0]
#     filled_clusters = associate_traj_cluster(df, best_clustering)
#     df_filled_clusters = list_serie_to_df(filled_clusters)
#     for filled_df in df_filled_clusters:
#         filled_df.columns = df.columns
#     l = get_infos(pd.read_excel(excel_file), 'delta_T0')
#     l.sort()
#     sequences = []
#     for cluster in df_filled_clusters:
#         dic = fill_dic(n_sized_precedence(cluster, 1, 'delta_T0'))
#         sequences.append(find_seq_by_deltat0(l[0], l[-1], fill_dic(n_sized_precedence(cluster, 1, 'delta_T0'))))
#         pass
#     return sequences

def associate_traj_cluster(df, best_cluster, arg):
    if best_cluster != 1:
        filled_clusters = [[] for _ in range(best_cluster.n_clusters)]
        for index_traj, traj in df.iterrows():
            # TODO for each trajectory, take the delta t0, find its index in bst_cluster.X_fit
            cluster_index = np.where(best_cluster.X_fit_ == traj[arg])  # gets all indexes verifying the property
            filled_clusters[best_cluster.labels_[cluster_index[0][0]]].append(traj)
        return filled_clusters
    else:
        return 0


def select_collisions(dic):
    # for key in dic.keys():
    #     if len(dic[key]) < 2:
    #         del d2[key]
    return {k: v for k, v in dic.items() if len(v) > 1}


def pattern_for_each_cluster_coin(df):
    """
    :return: list of dictionnaries, with all coincidences for each cluster
    """
    best_clustering = choose_timelapses(df)[0]
    filled_clusters = associate_traj_cluster(df, best_clustering, 'delta_T0')
    if filled_clusters != 0:
        df_filled_clusters = list_serie_to_df(filled_clusters)
        for filled_df in df_filled_clusters:
            filled_df.columns = df.columns
        sequences = []
        for cluster in df_filled_clusters:
            sequences.append(select_collisions(n_sized_coincidence(cluster)))
        return sequences
    else:
        return 0


def draw_clustering_complexity(df, step=1, title="", n_tries=0, treshold=1.00001, option="show", output_file=""):
    df_list = []
    X = []
    Y = []
    if not n_tries:
        n_tries = len(df['delta_T0']) - 2
    for index in range(2, n_tries, step):
        df_list.append(df.iloc[:index])
    for index, frame in enumerate(df_list):
        t1 = time()
        choose_timelapses(frame, treshold, n_tries)
        t2 = time()
        nb_samples = len(frame['delta_T0'])
        X.append(nb_samples)
        Y.append(t2 - t1)
    plt.plot(X, Y)
    plt.title(title)
    plt.xlabel('number of samples')
    plt.ylabel('complexity (seconds)')
    if option == "show":
        plt.show()
    elif option == "savefig":
        plt.savefig(output_file)
    else:
        print("Invalid option")
        return 1


# def func_complexity(func, column, func_arg, x_label, y_label, option):
#     df_list = []
#     if not n_tries:
#         n_tries = len(df['delta_T0']) - 2
#     for index in range(2, n_tries, step):
#         df_list.append(df.iloc[:index])
#     for index, frame in enumerate(df_list):
#         t1 = time()
#         function(frame, treshold, n_tries)
#         t2 = time()
#         print(t2 - t1)
#         nb_samples = len(frame['delta_T0'])
#         X.append(nb_samples)
#         Y.append(t2 - t1)
#     plt.plot(X, Y)
def to_excel_complexity(df, output_file, step=1, first_index=0, last_index=0):
    """
    time to find all coincidences in df.
    :param df:
    :param output_file:
    :param step:
    :param first_index:
    :param last_index:
    :return:
    """
    df_list = []
    if not last_index:
        last_index = len(df['delta_T0']) - 2
    for index in range(first_index, last_index, step):
        df_list.append(df.iloc[:index])
    data = []
    for index, frame in enumerate(df_list):
        t1 = time()
        all_seqs = pattern_for_each_cluster_coin(frame)
        # if all_seqs != 0:
        #     long_seqs = []
        #     for el in all_seqs:
        #         long_seqs.append(select_collisions(el))
        t2 = time()
        nb_samples = len(frame['delta_T0'])
        data.append([t2 - t1, nb_samples])
    df = pd.DataFrame(data, index=range(len(data)), columns=['time', 'medical statement count'])
    df.to_excel(output_file)


def main():
    # ti = time()
    # # # X = to_time_series_dataset([[1], [1], [1], [5], [50], [51], [52], [53], [200], [200.1], [200.2]])
    # # # km = TimeSeriesKMeans(n_clusters=4, verbose=False, max_iter=5, metric="dtw", random_state=0).fit(X)
    # # t2 = time()
    # # #timelapses = choose_timelapses('bio_ precede_full3.xlsx')
    # # cluster, sil_score = choose_timelapses('test.xlsx')
    # # # cluster, sil_score = choose_timelapses('bio_precede_full3.xlsx')
    # # t3 = time()
    # # print(t3 - t2)
    # # t1 = time()
    # in_df = pd.read_excel('bio_coincide_full3.xlsx')
    # df = in_df[:150]
    # # t1 = time()
    # #l = pattern_for_each_cluster_coin(df)
    # choose_timelapses(df)
    # # l = n_sized_coincidence(df)
    # # t2 = time()
    # # print("draw_time = {}".format(t2-t1))
    # # df = pd.read_excel('bio_precede_full3.xlsx')
    # # df = pd.read_excel('test.xlsx')
    # # best_clustering = choose_timelapses(df)[0]
    # # filled_clusters = associate_traj_cluster(df, best_clustering)
    # # df1 = pd.read_excel('test.xlsx')
    # # seqs = pattern_for_each_cluster_prec('test.xlsx')
    # # data = [['hey', 1], ['aaa', 2]]
    # # s = pd.Series(data, index=['delta_T0', 'b'])
    # # a = s['b']
    # # date = date_coin(s)
    # # data = [['hey' for _ in range(15)]]
    # # df = pd.DataFrame(data)
    # # df.columns = df1.columns
    # # t1 = time()
    # # df = pd.read_excel('coincide_test.xlsx')
    # # all_seqs = pattern_for_each_cluster_coin(df)
    # # long_seqs = []
    # # for el in all_seqs:
    # #     long_seqs.append(select_collisions(el))
    # # t2 = time()
    # # print(" find coincidences in {} for {} lines ".format(t2 - t1, len(df['Source'])))
    # # to_excel_complexity('coincide_test.xlsx', 'coincidences_times.xlsx', 10, 2, 100)
    # # t2 = time()
    # # print(t2-ti)
    # # to_excel_complexity('coincide_test.xlsx', 'coincidences_times.xlsx', 10, 300, 400)
    # # t1 = time()
    # # draw_coincidence_complexity('coincide_test.xlsx', 20)
    # # t2 = time()
    # print(t2-t1)
    # ti = time()
    t1 = time()
    df = pd.read_excel('bio_coincide_full3.xlsx')
    t2 = time()
    print(t2 - t1)
    # d = df[:100]
    # t1 = time()
    # draw_sil_complexity(df[:10000])
    # # print("read_excel time : {}".format(t1 - ti))
    # # output_file = "test.png"
    # # choose_timelapses(df, 2, 40000)
    # # draw_clustering_complexity(df, 10, "optimised cluster & sil score", 1000)
    # tf = time()
    # print("draw_cluster : {}".format(tf - t1))

    """
    modify size of samples
    """
    # x = []
    # c = 0
    # for longueur in range(100, 20000, 1000):
    #     array = get_infos(df[:longueur], 'delta_T0')
    #     ndarray = [[el] for el in array]
    #     timeserie = to_time_series_dataset(ndarray)
    #     cluster = TimeSeriesKMeans(n_clusters=4, verbose=False, max_iter=5, metric="dtw", random_state=0).fit(
    #         timeserie)
    #     ta = time()
    #     silhouette_score(timeserie, cluster.labels_)
    #     tb = time()
    #     print(tb - ta)
    #     c += 1
    #     x.append(tb - ta)
    # y = range(c)
    # plt.xlabel("number of samples")
    # plt.ylabel("silouhette score calculation")
    # plt.plot(x, y)
    # plt.show()
    """
    modify n clusters
    """
    y = []
    c = 0
    array = get_infos(df[:500], 'delta_T0', False)
    ndarray = [[el] for el in array]
    timeserie = to_time_series_dataset(ndarray)
    for n_cluster in range(2, len(array), 100):
        print(n_cluster)
        cluster = TimeSeriesKMeans(n_clusters=n_cluster, verbose=False, max_iter=5, metric="dtw", random_state=0).fit(
            timeserie)
        ta = time()
        silhouette_score(timeserie, cluster.labels_)
        tb = time()
        y.append(tb - ta)
        c += 1
    x = range(c)
    plt.xlabel("number of clusters")
    plt.ylabel("silouhette score calculation")
    plt.plot(x, y)
    plt.savefig('silhouette_score_calc.png')
    print("test passed")


main()
