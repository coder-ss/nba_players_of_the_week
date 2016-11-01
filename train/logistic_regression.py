import sys
import os
import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
import math


def is_candidate(player):
    """通过显而易见的数据把不可能是周最佳的球员排除在外

    :param player: 球员这一周的平均数据
    :return: 球员是否可能是周最佳候选人
    """
    if float(player['win_pct']) < 0.3 or float(player['minutes_played']) < 20 \
            or float(player['points']) < 12 or float(player['game_score']) < 12:
    # if float(player[5]) < 0.3 or float(player[7]) < 20 \
    #         or float(player[25]) < 13 or float(player[26]) < 13:
        return False
    else:
        return True


def load_train_data(fn):
    data_this_week_arr = []
    label_this_week_arr = []
    info_this_week_arr = []
    d_w = []; d_e = []
    l_w = []; l_e = []
    i_w = []; i_e = []

    path = '%s/data/train/' % (os.path.dirname(sys.path[0]))
    with open('%s%s' % (path, fn), 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if not is_candidate(row):
                continue

            _opp_win_pct = float(row['opp_win_pct']) if float(row['opp_win_pct']) == 0.0 else math.log(float(row['opp_win_pct']))
            _my_score = float(row['points']) + 1.5 * float(row['total_rebounds']) + 2 * float(row['assists']) + 2 * float(row['steals']) + 2 * float(row['blocks'])

            # tmp_data = [float(row['total_rebounds'])**2, float(row['assists'])**2,
            #             math.log(float(row['win_pct'])) * float(row['win_count']),
            #             _my_score, _my_score / float(row['minutes_played']),
            #             row['win_count'], math.log(float(row['win_pct'])), row['his_win_pct'],
            #             _opp_win_pct,
            #             row['minutes_played'], math.log(float(row['field_goal_pct'])),
            #             row['free_throw_pct'], row['total_rebounds'],
            #             row['steals'], row['blocks'], row['turnovers'],row['personal_fouls'],
            #             row['points'], row['game_score'], row['plus_minus'], pow(float(row['plus_minus']), 3),
            #             pow(float(row['plus_minus']), 5)]
            tmp_data = [row['win_count'], row['win_pct'], row['his_win_pct'],row['opp_win_pct'],
                        row['minutes_played'], row['field_goal_pct'],
                        row['free_throw_pct'],
                        row['total_rebounds'], row['assists'],
                        row['steals'], row['blocks'], row['turnovers'], row['personal_fouls'],
                        row['points'], row['game_score'], row['plus_minus'],
                        # row['var_opp_win_pct'],
                        # row['var_minutes_played'], row['var_field_goal_pct'],
                        # row['var_free_throw_pct'], row['var_total_rebounds'], row['var_assists'],
                        # row['var_steals'], row['var_blocks'], row['var_turnovers'], row['var_personal_fouls'],
                        # row['var_points'], row['var_game_score'], row['var_plus_minus']
                        ]

            if row['area'] == 'W':
                d_w.append(tmp_data)
                l_w.append(row['is_pow'])
                i_w.append(row)
            else:
                d_e.append(tmp_data)
                l_e.append(row['is_pow'])
                i_e.append(row)

            # data_this_week_arr.append(tmp_data)
            # label_this_week_arr.append(row['is_pow'])
            # info_this_week_arr.append(row)
    data_this_week_arr.extend(scale_trans(d_w))
    data_this_week_arr.extend(scale_trans(d_e))
    label_this_week_arr.extend(l_w)
    label_this_week_arr.extend(l_e)
    info_this_week_arr.extend(i_w)
    info_this_week_arr.extend(i_e)

    return data_this_week_arr, label_this_week_arr, info_this_week_arr


def scale_trans(data_set):
    data_set_arr = np.array(data_set).astype(np.float)
    data_mean = np.mean(data_set_arr, 0)
    data_var = np.var(data_set_arr, 0)
    data_set_arr = (data_set_arr - data_mean) # / data_var

    return data_set_arr


def load_data(test_rate=0.1):
    path = '%s/data/train/' % (os.path.dirname(sys.path[0]))

    test_file_arr = []
    train_file_arr = []

    for filename in os.listdir(path):
        if filename[-3:] != 'csv'\
                or filename.replace('data_', '').replace('.csv', '') > '2016-10-20'\
                or filename.replace('data_', '').replace('.csv', '') < '2012-10-20':
            continue
        train_file_arr.append(filename)

    count_test = int(test_rate * len(train_file_arr))
    for i in range(count_test):
        rand_index = int(np.random.uniform(0, len(train_file_arr)))
        test_file_arr.append(train_file_arr[rand_index])
        del train_file_arr[rand_index]

    x_arr = []
    y_arr = []
    for filename in train_file_arr:
        x_this_week_arr, y_this_week_arr, info_this_week_arr = load_train_data(filename)
        x_arr.extend(x_this_week_arr)
        y_arr.extend(y_this_week_arr)
    x_arr = np.array(x_arr)
    y_arr = np.array(y_arr).astype(np.int)

    test_x_arr = []
    test_y_arr = []
    test_info_arr = []
    test_date = []
    for filename in test_file_arr:
        x_this_week_arr, y_this_week_arr, info_this_week_arr = load_train_data(filename)
        test_x_arr.append(x_this_week_arr)
        test_y_arr.append(y_this_week_arr)
        test_info_arr.append(info_this_week_arr)
        test_date.append(filename.replace('.csv', '').replace('data_', ''))

    return x_arr, y_arr, test_x_arr, test_y_arr, test_info_arr, test_date


def cmp_func(a, b):
    return a['prob'] - b['prob']


if __name__ == '__main__':
    total_rs = []

    for m in range(30):
        x_arr, y_arr, test_x_arr, test_y_arr, test_info_arr,test_date = load_data()

        # poly = PolynomialFeatures(degree=2, interaction_only=True)

        classifier = LogisticRegression(class_weight='balanced')
        # classifier.fit(poly.fit_transform(x_arr), y_arr)
        classifier.fit(x_arr, y_arr)

        # 每周分别预测
        rs_dict = {}
        for i in range(len(test_x_arr)):
            # print(test_date[i])

            # rs = classifier.predict_proba(poly.fit_transform(test_x_arr[i]))
            rs = classifier.predict_proba(test_x_arr[i])

            rs_list_w = []
            rs_list_e = []

            for j in range(len(test_x_arr[i])):
                tmp_tuple = (test_info_arr[i][j]['team_id'], test_info_arr[i][j]['name'],
                             test_info_arr[i][j]['win_count'],
                             '%.2f' % float(test_info_arr[i][j]['win_pct']),
                             '%.2f' % float(test_info_arr[i][j]['his_win_pct']),
                             '%.2f' % float(test_info_arr[i][j]['opp_win_pct']),
                             '%.2f' % float(test_info_arr[i][j]['field_goal_pct']),
                             '%.2f' % float(test_info_arr[i][j]['points']),
                             '%.2f' % float(test_info_arr[i][j]['total_rebounds']), '%.2f' % float(test_info_arr[i][j]['assists']),
                             '%.2f' % float(test_info_arr[i][j]['steals']), '%.2f' % float(test_info_arr[i][j]['blocks'],),
                             '%.2f' % float(test_info_arr[i][j]['plus_minus'], ),
                             test_y_arr[i][j], '%.3f' % rs[j][1]
                             )

                if test_info_arr[i][j]['area'] == 'W':
                    rs_list_w.append(tmp_tuple)
                else:
                    rs_list_e.append(tmp_tuple)

            rs_list_w = sorted(rs_list_w, key=lambda l: l[-1], reverse=True)
            rs_list_e = sorted(rs_list_e, key=lambda l: l[-1], reverse=True)

            rank_w = 0
            for r in rs_list_w:
                rank_w += 1
                # print(str(r))
                if int(r[-2]) == 1:
                    break
            rs_dict[rank_w] = rs_dict.get(rank_w, 0) + 1

            # print('-----------------------------------------------------------')

            rank_e = 0
            for r in rs_list_e:
                rank_e += 1
                # print(r)
                if int(r[-2]) == 1:
                    break
            # print('')
            rs_dict[rank_e] = rs_dict.get(rank_e, 0) + 1

        max = 0
        for k in rs_dict:
            if max < k:
                max = k

        rs_list = [0] * (max + 1)

        for k in rs_dict:
            rs_list[k] = rs_dict[k]
        print(rs_list[1:])

        rs_arr = np.array(rs_list)
        _sum = np.sum(rs_arr)
        # print('预测正确的概率：%.2f' % (float(rs_list[1] / _sum)))
        # print('预测在前两位的概率：%.2f' % (float(rs_list[1] / _sum) + float(rs_list[2] / _sum)))
        # print('预测在前三位的概率：%.2f' % (float(rs_list[1] / _sum) + float(rs_list[2] / _sum) + float(rs_list[3] / _sum)))

        total_rs.append([float(rs_list[1] / _sum), float(rs_list[1] / _sum) + float(rs_list[2] / _sum), float(rs_list[1] / _sum) + float(rs_list[2] / _sum) + float(rs_list[3] / _sum)])

    total_arr = np.array(total_rs)
    print(np.mean(total_arr, 0))
