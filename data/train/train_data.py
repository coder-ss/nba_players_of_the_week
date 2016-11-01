import csv
import sys
import datetime
import os
import numpy as np


def get_team_area():
    """ 获取球队属于东部还是西部

    :return: dict
    """
    long_to_area = {}
    with open('%s/teams/teams_area.csv' % os.path.dirname(sys.path[0]), 'r') as _csvfile:
        _reader = csv.DictReader(_csvfile)
        for _row in _reader:
            long_to_area[_row['name']] = _row['area']

    short_to_area = {}
    with open('%s/teams/teams.csv' % os.path.dirname(sys.path[0]), 'r') as _csvfile:
        _reader = csv.DictReader(_csvfile)
        for _row in _reader:
            short_to_area[_row['%s_short' % year]] = long_to_area[_row['name']]

    return short_to_area


def get_team_win_pct(_year):
    """ 获取指定赛季 每个球队 截止到每个评奖日期的胜率

    :param _year: 赛季 2016表示2015-16赛季
    :return: dict
    """
    _d = {}
    with open('%s/win_pct/win_pct_%s.csv' % (os.path.dirname(sys.path[0]), _year), 'r') as _csvfile:
        _reader = csv.DictReader(_csvfile)
        for _row in _reader:
            _d[_row['team']] = _d.get(_row['team'], {})

            if float(_row['count']) - float(_row['cur_count']) != 0.0:
                _pre_pct = (float(_row['win']) - float(_row['cur_win'])) / (float(_row['count']) - float(_row['cur_count']))
            else:
                _pre_pct = 0.0
            _d[_row['team']][_row['date']] = _pre_pct
    return _d


def get_pows_and_sundays(_year):
    """ 获取指定赛季的周最佳 和 周最佳评选日期（周日）

    :param _year: 赛季 2016表示2015-16赛季
    :return: 该赛季的周最佳，周最佳评选日期
    """
    dt_begin = datetime.datetime.strptime('%s-10-20' % (_year - 1), '%Y-%m-%d')
    dt_end = datetime.datetime.strptime('%s-05-01' % _year, '%Y-%m-%d')

    season_pows = {}  # 这个赛季的所有周最佳
    sundays_dict = {}  # 标注评选周最佳的日期
    with open('%s/players_of_week/pows.csv' % os.path.dirname(sys.path[0]), 'r') as _csvfile:
        _reader = csv.DictReader(_csvfile)

        for _row in _reader:
            dt_sunday = datetime.datetime.strptime(_row['date'], '%Y-%m-%d')

            if dt_begin <= dt_sunday <= dt_end:
                sundays_dict[int(datetime.datetime.strptime(_row['date'], '%Y-%m-%d').timestamp())] = _row['date']
                season_pows[_row['date']] = season_pows.get(_row['date'], {})
                season_pows[_row['date']][_row['uri']] = 1

    _sundays = [[k, sundays_dict[k]] for k in sorted(sundays_dict.keys())]

    return season_pows, _sundays


def to_sunday(sundays, dt_game):
    """ 将比赛日期 映射到 相应的评奖日期

    :param sundays: 评奖日期list
    :param dt_game: 比赛日期
    :return:
    """
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


def minutes_played(str):
    try:
        arr = str.split(':')

        rs = float(arr[0])
        rs += float(arr[0]) / 60
        return rs
    except Exception as e:
        return 0.0


def compute_avg(_data_list, _year):
    if not _data_list['data']:
        return []

    _keys = ['minutes_played', 'field_goals', 'field_goal_attempts', 'field_goal_pct',
             'three_point_field_goals', 'three_point_field_goal_attempts', 'three_point_field_goal_pct',
             'free_throws', 'free_throw_attempts', 'free_throw_pct',
             'offensive_rebounds', 'defensive_rebounds', 'total_rebounds',
             'assists', 'steals', 'blocks', 'turnovers',
             'personal_fouls', 'points', 'game_score',
             'plus_minus',
             'daily_fantasy_sports_points','opp_win_pct'
             ]

    _list = []
    _tj = {'team_id':_data_list['team_id'], 'area':_data_list['area'], 'name':_data_list['name'],
           'game_count': 0, 'win_count': 0, 'started_count': 0,
           'uri':_data_list['uri'], 'is_pow':_data_list['is_pow']
           }
    for _game_data in _data_list['data']:
        _game_data['minutes_played'] = minutes_played(_game_data['minutes_played'])
        _list.append([_game_data[_k] for _k in _keys])

        _tj['game_count'] += 1
        if _game_data['game_result'].strip()[:1] == 'W':
            _tj['win_count'] += 1
        _tj['started_count'] += int(_game_data['games_started'])

    _arr = np.array(_list)
    _arr[_arr==''] = 0.0
    _arr = _arr.astype(np.float)
    _arr_mean = np.mean(_arr, 0)
    _arr_var = np.var(_arr, 0)

    for i in range(len(_keys)):
        _tj[_keys[i]] = _arr_mean[i]
    for i in range(len(_keys)):
        _tj['var_%s' % _keys[i]] = _arr_var[i]
    # if _year != 2016:
        # _tj['daily_fantasy_sports_points'] = ''
    _tj['win_pct'] = float(_tj['win_count']) / float(_tj['game_count'])
    _tj['his_win_pct'] = _data_list['his_win_pct']
    return _tj


def compute_player_data(_year, _team_to_area, _pows_season, _sundays, _win_pct):
    _week_avg_dict = {}

    with open('%s/gamelogs/gamelogs_%s.csv' % (os.path.dirname(sys.path[0]), _year), 'r') as _csvfile:
        _reader = csv.DictReader(_csvfile)

        for _row in _reader:
            # 找到比赛所属的那周
            _cur_sunday = to_sunday(_sundays, _row['date_game'])
            _week_avg_dict[_cur_sunday] = _week_avg_dict.get(_cur_sunday, {})

            player_key = '%s_%s' % (_row['team_id'], _row['name'])
            _week_avg_dict[_cur_sunday][player_key] = _week_avg_dict[_cur_sunday].get(player_key, {
                'team_id': _row['team_id'],
                'area': _team_to_area[_row['team_id']],
                'name': _row['name'],
                'uri': _row['uri'],
                'is_pow': (1 if _row['uri'] in _pows_season[_cur_sunday].keys() else 0),
                'his_win_pct': _win_pct[_row['team_id']][_cur_sunday],
                'data': []
            })
            if _row['game_season'].isdigit() and minutes_played(_row['minutes_played']) > 0.0:
                _row['opp_win_pct'] = _win_pct[_row['opp_id']][_cur_sunday]
                _week_avg_dict[_cur_sunday][player_key]['data'].append(_row)

    rs = {}
    for _cur_sunday in _week_avg_dict:
        _week_avg_arr = []
        for player_key in _week_avg_dict[_cur_sunday]:
            _player_avg = compute_avg(_week_avg_dict[_cur_sunday][player_key], year)

            if _player_avg:
                _week_avg_arr.append(_player_avg)
        # print(_week_avg_arr)
        rs[_cur_sunday] = _week_avg_arr
        # break
    return rs


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('please input the year. example: 2016 represent the season of 2015-2016')
        exit()
    if 2013 > int(sys.argv[1]) or int(sys.argv[1]) > 2016:
        print('the year must in 2013-2016')
        exit()

    year = int(sys.argv[1])

    # 获取球队属于东部还是西部
    team_to_area = get_team_area()

    # 获取该赛季的周最佳 和 周最佳评选日期（周日）
    pows_season, sundays = get_pows_and_sundays(year)

    # 获取该赛季 各球队各阶段的胜率
    win_pct = get_team_win_pct(year)

    # 计算每周每个球员的平均数据（用于训练的最终数据）
    week_avg_data = compute_player_data(year, team_to_area, pows_season, sundays, win_pct)

    for cur_sunday in week_avg_data:
        path = '%s/data_%s.csv' % (sys.path[0], cur_sunday)
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['team_id', 'area', 'name', 'game_count', 'win_count', 'win_pct',
                          'his_win_pct', 'opp_win_pct', 'started_count',
                          'minutes_played', 'field_goals', 'field_goal_attempts', 'field_goal_pct',
                          'three_point_field_goals', 'three_point_field_goal_attempts',
                          'three_point_field_goal_pct', 'free_throws', 'free_throw_attempts',
                          'free_throw_pct', 'offensive_rebounds', 'defensive_rebounds', 'total_rebounds',
                          'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls', 'points', 'game_score',
                          'plus_minus', 'daily_fantasy_sports_points',
                          'var_minutes_played', 'var_field_goals', 'var_field_goal_attempts', 'var_field_goal_pct',
                          'var_three_point_field_goals', 'var_three_point_field_goal_attempts', 'var_three_point_field_goal_pct',
                          'var_free_throws', 'var_free_throw_attempts', 'var_free_throw_pct',
                          'var_offensive_rebounds', 'var_defensive_rebounds', 'var_total_rebounds',
                          'var_assists', 'var_steals', 'var_blocks', 'var_turnovers',
                          'var_personal_fouls', 'var_points', 'var_game_score',
                          'var_plus_minus',
                          'var_daily_fantasy_sports_points', 'var_opp_win_pct',
                          'uri', 'is_pow']

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(week_avg_data[cur_sunday])
