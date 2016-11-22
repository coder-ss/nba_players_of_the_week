import requests
from bs4 import BeautifulSoup
import csv
import sys
import os
import re
import queue
import threading


def crawl_gamelogs(name, uri, year):
    _url = 'http://www.basketball-reference.com%s/gamelog/%s/' % (uri.replace('.html', ''), year)  # /players/h/horfoal01
    _headers = {'Host': 'www.basketball-reference.com',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                'Cookie': ''}

    try:
        r = requests.get(_url, headers=_headers, timeout=60)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')

        div = soup.find('div', attrs={'id': 'all_pgl_basic'})
        trs = div.find('tbody').find_all("tr", id=re.compile('pgl_basic\.\d*'))
    except Exception as e:
        print('aa', e)
        return []

    gls = []
    for tr in trs:
        if tr.find(attrs={'data-stat': 'game_season'}).find('strong').string is None:
            game_season = tr.find(attrs={'data-stat': 'reason'}).string
        else:
            game_season = tr.find(attrs={'data-stat': 'game_season'}).find('strong').string

        gl = {
            'name': name,
            'ranker': tr.find(attrs={'data-stat': 'ranker'}).string,
            'game_season': game_season,
            'date_game': tr.find(attrs={'data-stat': 'date_game'}).find('a').string,
            'age': tr.find(attrs={'data-stat': 'age'}).string,
            'team_id': tr.find(attrs={'data-stat': 'team_id'}).find('a').string,
            'game_location': tr.find(attrs={'data-stat': 'game_location'}).string,
            'opp_id': tr.find(attrs={'data-stat': 'opp_id'}).find('a').string,
            'game_result': tr.find(attrs={'data-stat': 'game_result'}).string,
            'games_started': '',
            'minutes_played': '',
            'field_goals': '',
            'field_goal_attempts': '',
            'field_goal_pct': '',
            'three_point_field_goals': '',
            'three_point_field_goal_attempts': '',
            'three_point_field_goal_pct': '',
            'free_throws': '',
            'free_throw_attempts': '',
            'free_throw_pct': '',
            'offensive_rebounds': '',
            'defensive_rebounds': '',
            'total_rebounds': '',
            'assists': '',
            'steals': '',
            'blocks': '',
            'turnovers': '',
            'personal_fouls': '',
            'points': '',
            'game_score': '',
            'plus_minus': '',
            'daily_fantasy_sports_points': '',
            'uri': uri,
        }
        if tr.find(attrs={'data-stat': 'game_season'}).find('strong').string is not None:
            gl['games_started'] = tr.find(attrs={'data-stat': 'gs'}).string
            gl['minutes_played'] = tr.find(attrs={'data-stat': 'mp'}).string
            gl['field_goals'] = tr.find(attrs={'data-stat': 'fg'}).string
            gl['field_goal_attempts'] = tr.find(attrs={'data-stat': 'fga'}).string
            gl['field_goal_pct'] = tr.find(attrs={'data-stat': 'fg_pct'}).string
            gl['three_point_field_goals'] = tr.find(attrs={'data-stat': 'fg3'}).string
            gl['three_point_field_goal_attempts'] = tr.find(attrs={'data-stat': 'fg3a'}).string
            gl['three_point_field_goal_pct'] = tr.find(attrs={'data-stat': 'fg3_pct'}).string
            gl['free_throws'] = tr.find(attrs={'data-stat': 'ft'}).string
            gl['free_throw_attempts'] = tr.find(attrs={'data-stat': 'fta'}).string
            gl['free_throw_pct'] = tr.find(attrs={'data-stat': 'ft_pct'}).string
            gl['offensive_rebounds'] = tr.find(attrs={'data-stat': 'orb'}).string
            gl['defensive_rebounds'] = tr.find(attrs={'data-stat': 'drb'}).string
            gl['total_rebounds'] = tr.find(attrs={'data-stat': 'trb'}).string
            gl['assists'] = tr.find(attrs={'data-stat': 'ast'}).string
            gl['steals'] = tr.find(attrs={'data-stat': 'stl'}).string
            gl['blocks'] = tr.find(attrs={'data-stat': 'blk'}).string
            gl['turnovers'] = tr.find(attrs={'data-stat': 'tov'}).string
            gl['personal_fouls'] = tr.find(attrs={'data-stat': 'pf'}).string
            gl['points'] = tr.find(attrs={'data-stat': 'pts'}).string
            gl['game_score'] = tr.find(attrs={'data-stat': 'game_score'}).string
            gl['plus_minus'] = tr.find(attrs={'data-stat': 'plus_minus'}).string
            try:
                gl['daily_fantasy_sports_points'] = tr.find(attrs={'data-stat': 'dfs'}).string
            except Exception as e:
                # print('bb', e)
                pass
        gls.append(gl)
        # print(gl)
    return gls


def run(q1, q2, year):
    while not q1.empty():
        row = q1.get()

        gls = []
        count = 0
        while len(gls) == 0 and count < 5:
            count += 1
            gls = crawl_gamelogs(row['name'], row['uri'], year)
        print(count, row['team'], row['name'], 'crawl game logs. count:', len(gls))

        for gl in gls:
            q2.put(gl)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('please input the year. example: 2016 represent the season of 2015-2016')
        exit()
    if 2002 > int(sys.argv[1]) or int(sys.argv[1]) > 2016:
        print('the year must in 2013-2016')
        exit()

    path = '%s/players/players_%s.csv' % (os.path.dirname(sys.path[0]), sys.argv[1])
    path_save = '%s/gamelogs_%s.csv' % (sys.path[0], sys.argv[1])

    fieldnames = ['name', 'ranker', 'game_season', 'date_game', 'age', 'team_id', 'game_location',
                  'opp_id', 'game_result', 'college_name', 'games_started', 'minutes_played', 'field_goals',
                  'field_goal_attempts', 'field_goal_pct', 'three_point_field_goals', 'three_point_field_goal_attempts',
                  'three_point_field_goal_pct', 'free_throws', 'free_throw_attempts', 'free_throw_pct',
                  'offensive_rebounds', 'defensive_rebounds', 'total_rebounds', 'assists', 'steals', 'blocks', 'turnovers',
                  'personal_fouls', 'points', 'game_score', 'plus_minus', 'daily_fantasy_sports_points', 'uri']

    existed = {}
    if not os.path.exists(path_save):
        with open(path_save, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    else:
        with open(path_save, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existed[row['uri']] = existed.get(row['uri'], {'count':0})
                existed[row['uri']]['count'] += 1
                _game_id = '%s_%s' % (row['date_game'], row['team_id'])
                existed[row['uri']][_game_id] = 1

    queue_players = queue.Queue()
    queue_gamelogs = queue.Queue()
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        count = 0
        players = {}  # 防止同一球员抓多次
        for row in reader:
            if row['uri'] in existed.keys():
                if len(sys.argv) > 2 and sys.argv[2] == 'verify':
                    if existed[row['uri']]['count'] == 82:
                        continue
                else:
                    continue

            players[row['uri']] = row

        for id in players:
            print(players[id]['team'], players[id]['name'], 'put queue')
            queue_players.put(players[id])

    thrs = []
    thread_count = 5
    for i in range(thread_count):
       thrs.append(threading.Thread(target=run, args=(queue_players, queue_gamelogs, sys.argv[1])))
    for i in range(thread_count):
        thrs[i].setDaemon(True)
        thrs[i].start()

    with open(path_save, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        while threading.activeCount() > 1 or queue_gamelogs.qsize() > 0:
            row = queue_gamelogs.get()

            _game_id = '%s_%s' % (row['date_game'], row['team_id'])
            if row['uri'] in existed.keys() and _game_id in existed[row['uri']].keys():
                #print(row['name'], row['team_id'], row['date_game'], 'existed')
                pass
            else:
                #print(row['name'], row['team_id'], row['date_game'], 'save')
                writer.writerow(row)

    print('end')
