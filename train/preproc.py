import sys
import os
import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures


def is_candidate(player):
    """通过显而易见的数据把不可能是周最佳的球员排除在外

    :param player: 球员这一周的平均数据
    :return: 球员是否可能是周最佳候选人
    """
    # if float(player['win_pct']) < 0.3 or float(player['minutes_played']) < 20 \
    #         or float(player['points']) < 12 or float(player['game_score']) < 12:
    if float(player[5]) < 0.3 or float(player[7]) < 20 \
            or float(player[25]) < 13 or float(player[26]) < 13:
        return False
    else:
        return True


if __name__ == '__main__':
    path = '%s/data/train/' % (os.path.dirname(sys.path[0]))

    data_arr = []
    label_arr = []
    other_info_arr = []
    train_arr = []
    train_label = []
    test_arr = []
    test_label = []

    for filename in os.listdir(path):
        if filename[-3:] != 'csv':
            continue

        sunday = filename.replace('data_', '').replace('.csv', '')
        if sunday < '2014-10-20':
            continue

        data_week_arr = []
        label_week_arr = []
        other_info_week_arr = []

        with open('%s%s' % (path, filename), 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)

            line_count = 0
            for row in reader:
                line_count += 1
                if line_count == 1:
                    continue

                if not is_candidate(row):
                    continue

                label_week_arr.append(row[-1:][0])

                # tmp = float(row[19]) * 2 + float(row[20]) * 3 + float(row[21]) * 3 + float(row[22]) * 3 + float(row[23]) * -2 * float(row[24]) * -1.5 + float(row[25]) * 3
                # print(tmp)
                tmp_arr = row[3:-4]
                # tmp_arr.append(tmp)
                data_week_arr.append(tmp_arr)
                other_info_week_arr.append(row[0:3])

        data_arr.append(data_week_arr)
        label_arr.append(label_week_arr)
        other_info_arr.append(other_info_week_arr)

    test_count = 10
    test_index = {}

    while len(test_index) < test_count:
        rand_index = int(np.random.uniform(0, len(data_arr)))
        test_index[rand_index] = rand_index

    test_index_list = [k for k in sorted(test_index.keys())]

    for i in range(len(data_arr)):
        if i in test_index_list:
            test_arr.extend(data_arr[i])
            test_label.extend(label_arr[i])
        else:
            train_arr.extend(data_arr[i])
            train_label.extend(label_arr[i])

    train_arr2 = np.array(train_arr)
    # train_arr2[train_arr2 == ''] = 0.0
    train_arr2 = train_arr2.astype(np.float)
    train_label2 = np.array(train_label).astype(np.int)
    test_arr2 = np.array(test_arr)
    # test_arr2[test_arr2 == ''] = 0.0
    test_arr2 = test_arr2.astype(np.float)
    test_label2 = np.array(test_label).astype(np.int)

    # 对特征进行标准化处理，使每个特征具有相同的重要性
    # x_means = np.mean(train_arr2, 0)
    # x_var = np.var(train_arr2, 0)
    # train_arr2 = (train_arr2 - x_means) / x_var
    #
    # x_means = np.mean(test_arr2, 0)
    # x_var = np.var(test_arr2, 0)
    # test_arr2 = (test_arr2 - x_means) / x_var

    poly = PolynomialFeatures(degree=2, interaction_only=True)
    train_arr2= poly.fit_transform(train_arr2)
    test_arr2 = poly.fit_transform(test_arr2)

    classifier = LogisticRegression(class_weight={0:0.15,1:0.85})
    classifier.fit(train_arr2, train_label2)

    rs = classifier.predict_proba(test_arr2)

    k = 0
    for i in test_index_list:
        pow_w = {'name':'', 'prob':0.0}
        pow_e = {'name': '', 'prob': 0.0}

        real_w = ''
        real_e = ''

        for j in range(len(other_info_arr[i])):
            if other_info_arr[i][j][1] =='W':
                if rs[k][1] > pow_w['prob']:
                    pow_w['name'] = other_info_arr[i][j][2]
                    pow_w['prob'] = rs[k][1]
            else:
                if rs[k][1] > pow_e['prob']:
                    pow_e['name'] = other_info_arr[i][j][2]
                    pow_e['prob'] = rs[k][1]

            if int(label_arr[i][j]) == 1:
                if other_info_arr[i][j][1] == 'W':
                    real_w = other_info_arr[i][j][2]
                else:
                    real_e = other_info_arr[i][j][2]
            if rs[k][1] > 0.5:
                print(other_info_arr[i][j][0], other_info_arr[i][j][1], other_info_arr[i][j][2], label_arr[i][j], rs[k])
            k += 1
        print('Real POW_W: %s; POW_E: %s' % (real_w, real_e))
        print('Predict POW_W: %s; POW_E: %s' % (pow_w['name'], pow_e['name']))
        print('')
