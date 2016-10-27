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


def minutes_played(str):
    try:
        arr = str.split(':')

        rs = float(arr[0])
        rs += float(arr[0]) / 60
        return rs
    except Exception as e:
        return 0.0


def avg_date(avg_old, new_date):
    if not new_date['game_season'].isdigit():
        return

    mp = minutes_played(new_date['minutes_played'])
    if mp <= 0.0:
        return

    count0 = avg_old['game_count']

    avg_old['game_count'] += 1
    if new_date['game_result'].strip()[:1] == 'W':
        avg_old['win_count'] += 1
    avg_old['win_pct'] = float(avg_old['win_count']) / avg_old['game_count']
    avg_old['started_count'] += int(new_date['games_started'])
    avg_old['minutes_played'] = (avg_old['minutes_played'] * count0 + minutes_played(new_date['minutes_played'])) / avg_old['game_count']
    avg_old['field_goals'] = (avg_old['field_goals'] * count0 + float(new_date['field_goals'])) / avg_old['game_count']
    avg_old['field_goal_attempts'] = (avg_old['field_goal_attempts'] * count0 + float(new_date['field_goal_attempts'])) / avg_old['game_count']
    if avg_old['field_goal_attempts'] == 0.0:
        avg_old['field_goal_pct'] = 0.0
    else:
        avg_old['field_goal_pct'] = avg_old['field_goals'] / avg_old['field_goal_attempts']
    avg_old['three_point_field_goals'] = (avg_old['three_point_field_goals'] * count0 + float(new_date['three_point_field_goals'])) / avg_old['game_count']
    avg_old['three_point_field_goal_attempts'] = (avg_old['three_point_field_goal_attempts'] * count0 + float(new_date['three_point_field_goal_attempts'])) / avg_old['game_count']
    if avg_old['three_point_field_goal_attempts'] == 0.0:
        avg_old['three_point_field_goal_pct'] = 0.0
    else:
        avg_old['three_point_field_goal_pct'] = avg_old['three_point_field_goals'] / avg_old['three_point_field_goal_attempts']
    avg_old['free_throws'] = (avg_old['free_throws'] * count0 + float(new_date['free_throws'])) / avg_old['game_count']
    avg_old['free_throw_attempts'] = (avg_old['free_throw_attempts'] * count0 + float(new_date['free_throw_attempts'])) / avg_old['game_count']
    if avg_old['free_throw_attempts'] == 0.0:
        avg_old['free_throw_pct'] = 0.0
    else:
        avg_old['free_throw_pct'] = avg_old['free_throws'] / avg_old['free_throw_attempts']
    avg_old['offensive_rebounds'] = (avg_old['offensive_rebounds'] * count0 + float(new_date['offensive_rebounds'])) / avg_old['game_count']
    avg_old['defensive_rebounds'] = (avg_old['defensive_rebounds'] * count0 + float(new_date['defensive_rebounds'])) / avg_old['game_count']
    avg_old['total_rebounds'] = (avg_old['total_rebounds'] * count0 + float(new_date['total_rebounds'])) / avg_old['game_count']
    avg_old['assists'] = (avg_old['assists'] * count0 + float(new_date['assists'])) / avg_old['game_count']
    avg_old['steals'] = (avg_old['steals'] * count0 + float(new_date['steals'])) / avg_old['game_count']
    avg_old['blocks'] = (avg_old['blocks'] * count0 + float(new_date['blocks'])) / avg_old['game_count']
    avg_old['turnovers'] = (avg_old['turnovers'] * count0 + float(new_date['turnovers'])) / avg_old['game_count']
    avg_old['personal_fouls'] = (avg_old['personal_fouls'] * count0 + float(new_date['personal_fouls'])) / avg_old['game_count']
    avg_old['points'] = (avg_old['points'] * count0 + float(new_date['points'])) / avg_old['game_count']
    avg_old['game_score'] = (avg_old['game_score'] * count0 + float(new_date['game_score'])) / avg_old['game_count']
    if avg_old['plus_minus'] != '':
        try:
            avg_old['plus_minus'] = (avg_old['plus_minus'] * count0 + float(new_date['plus_minus'])) / avg_old['game_count']
        except Exception as e:
            avg_old['plus_minus'] = ''
    if avg_old['daily_fantasy_sports_points'] != '':
        try:
            avg_old['daily_fantasy_sports_points'] = (avg_old['daily_fantasy_sports_points'] + float(new_date['daily_fantasy_sports_points'])) / avg_old['game_count']
        except Exception as e:
            avg_old['daily_fantasy_sports_points'] = ''


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

    # 获取球队属于东部还是西部
    short_to_long = {}
    with open('%s/teams/teams.csv' % os.path.dirname(sys.path[0]), 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            short_to_long[row['%s_short' % year]] = row['name']
    long_to_area = {}
    with open('%s/teams/teams_area.csv' % os.path.dirname(sys.path[0]), 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            long_to_area[row['name']] = row['area']


    pows_season = {}  # 这个赛季的所有周最佳
    sundays_dict = {}  # 标注评选周最佳的日期
    with open('%s/players_of_week/pows.csv' % os.path.dirname(sys.path[0]), 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            dt_sunday = datetime.datetime.strptime(row['date'], '%Y-%m-%d')

            if dt_begin <= dt_sunday <= dt_end:
                sundays_dict[int(datetime.datetime.strptime(row['date'], '%Y-%m-%d').timestamp())] = row['date']
                pows_season[row['date']] = pows_season.get(row['date'], {})
                pows_season[row['date']][row['uri']] = 1

    sundays = [[k, sundays_dict[k]] for k in sorted(sundays_dict.keys())]
    print(sundays)

    clean_rs = {}

    with open('%s/gamelogs/gamelogs_%s.csv' % (os.path.dirname(sys.path[0]), year), 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # 找到比赛所属的那周
            cur_sunday = to_sunday(sundays, row['date_game'])
            clean_rs[cur_sunday] = clean_rs.get(cur_sunday, {})

            player_key = '%s_%s' % (row['team_id'], row['name'])
            clean_rs[cur_sunday][player_key] = clean_rs[cur_sunday].get(player_key, {
                'team_id': row['team_id'],
                'area': long_to_area[short_to_long[row['team_id']]],
                'name':row['name'],
                'game_count': 0,
                'win_count': 0,
                'win_pct': 0.0,
                'started_count': 0,
                'minutes_played': 0.0,
                'field_goals': 0.0,
                'field_goal_attempts': 0.0,
                'field_goal_pct': 0.0,
                'three_point_field_goals': 0.0,
                'three_point_field_goal_attempts': 0.0,
                'three_point_field_goal_pct': 0.0,
                'free_throws': 0.0,
                'free_throw_attempts': 0.0,
                'free_throw_pct': 0.0,
                'offensive_rebounds': 0.0,
                'defensive_rebounds': 0.0,
                'total_rebounds': 0.0,
                'assists': 0.0,
                'steals': 0.0,
                'blocks': 0.0,
                'turnovers': 0.0,
                'personal_fouls': 0.0,
                'points': 0.0,
                'game_score': 0.0,
                'plus_minus': 0.0,
                'daily_fantasy_sports_points': (0.0 if year == 2016 else ''),
                'uri': row['uri'],
                'is_pow': (1 if row['uri'] in pows_season[cur_sunday].keys() else 0)
            })
            avg_date(clean_rs[cur_sunday][player_key], row)

    for cur_sunday in clean_rs:
        path = '%s/data_%s.csv' % (sys.path[0], cur_sunday)
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['team_id', 'area', 'name', 'game_count', 'win_count', 'win_pct', 'started_count',
                          'minutes_played', 'field_goals', 'field_goal_attempts', 'field_goal_pct',
                          'three_point_field_goals', 'three_point_field_goal_attempts',
                          'three_point_field_goal_pct', 'free_throws', 'free_throw_attempts',
                          'free_throw_pct', 'offensive_rebounds', 'defensive_rebounds', 'total_rebounds',
                          'assists', 'steals', 'blocks', 'turnovers', 'personal_fouls', 'points', 'game_score',
                          'plus_minus', 'daily_fantasy_sports_points', 'uri', 'is_pow']

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(clean_rs[cur_sunday].values())
