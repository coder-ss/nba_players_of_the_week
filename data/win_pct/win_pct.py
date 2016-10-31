import csv
import sys
import datetime
import os


def to_sunday(sundays, dt_game):
    ts_game = int(datetime.datetime.strptime(dt_game, '%Y-%m-%d').timestamp())

    mid = int((0 + len(sundays)) / 2)

    if mid == 0:
        return sundays[mid][1]
    elif sundays[mid - 1][0] < ts_game <= sundays[mid][0]:
        return sundays[mid][1]
    elif sundays[mid-1][0] >= ts_game:
        return to_sunday(sundays[:mid], dt_game)
    else:
        return to_sunday(sundays[mid:], dt_game)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('please input the year. example: 2016 represent the season of 2015-2016')
        exit()
    if 2013 > int(sys.argv[1]) or int(sys.argv[1]) > 2016:
        print('the year must in 2013-2016')
        exit()

    year = int(sys.argv[1])

    dt_begin = datetime.datetime.strptime('%s-10-20' % (year - 1), '%Y-%m-%d')
    dt_end = datetime.datetime.strptime('%s-05-01' % year, '%Y-%m-%d')

    sundays_dict = {}  # 标注评选周最佳的日期
    with open('%s/players_of_week/pows.csv' % os.path.dirname(sys.path[0]), 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            dt_sunday = datetime.datetime.strptime(row['date'], '%Y-%m-%d')

            if dt_begin <= dt_sunday <= dt_end:
                sundays_dict[int(datetime.datetime.strptime(row['date'], '%Y-%m-%d').timestamp())] = row['date']

    sundays = [[k, sundays_dict[k]] for k in sorted(sundays_dict.keys())]
    print(sundays)

    clean_rs = {}

    win_pct = {}
    with open('%s/gamelogs/gamelogs_%s.csv' % (os.path.dirname(sys.path[0]), year), 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            win_pct[row['team_id']] = win_pct.get(row['team_id'], {})
            win_pct[row['team_id']][row['date_game']] = win_pct[row['team_id']].get(row['date_game'], 0)

            if win_pct[row['team_id']][row['date_game']] == 0:
                if row['game_result'][0:1] == 'W':
                    win_pct[row['team_id']][row['date_game']] = 1
                else:
                    win_pct[row['team_id']][row['date_game']] = -1

    rs = []
    for team_id in win_pct:
        tmp_dict = {}
        count = 0
        win = 0
        loss = 0

        sorted_game_date = sorted(win_pct[team_id].keys())
        last_sunday = ''
        cur_sunday = ''

        for game_date in sorted_game_date:
            count += 1
            if win_pct[team_id][game_date] == 1:
                win += 1
            else:
                loss += 1

            if last_sunday == '':
                last_sunday = to_sunday(sundays, game_date)
            cur_sunday = to_sunday(sundays, game_date)

            if cur_sunday != last_sunday:
                tmp_dict[last_sunday] = {'team':team_id, 'date':last_sunday,'count':count, 'win':win, 'loss':loss}
                last_sunday = cur_sunday

        if cur_sunday not in tmp_dict.keys():
            tmp_dict[cur_sunday] = {'team':team_id, 'date':cur_sunday,'count': count, 'win': win, 'loss': loss}

        tmp_list = [tmp_dict[k] for k in sorted(tmp_dict)]

        rs.extend(tmp_list)

    path = '%s/win_pct_%s.csv' % (sys.path[0], year)
    with open(path, 'w', newline='') as csvfile:
        fieldnames = ['team', 'date', 'count', 'win', 'loss']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rs)
