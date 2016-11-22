import requests
from bs4 import BeautifulSoup
import csv
import sys
import os


def crawl_players(short_team, team, year):
    _url = 'http://www.basketball-reference.com/teams/%s/%s.html' % (short_team, year)  # /teams/BRK/2016.html
    _headers = {'Host': 'www.basketball-reference.com',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                'Cookie': ''}

    r = requests.get(_url, headers=_headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.find(attrs={'id': 'roster'})

    try:
        trs = table.find('tbody').find_all("tr")
    except Exception as e:
        return []

    ps = []
    for tr in trs:
        _a = tr.find("a")
        p = {
            'name': _a.string,
            'team': team,
            'short_team': short_team,
            'number': tr.find(attrs={'data-stat': 'number'}).string,
            'pos': tr.find(attrs={'data-stat': 'pos'}).string,
            'height': tr.find(attrs={'data-stat': 'height'}).string,
            'weight': tr.find(attrs={'data-stat': 'weight'}).string,
            'birth_date': tr.find(attrs={'data-stat': 'birth_date'}).string,
            'birth_country': tr.find(attrs={'data-stat': 'birth_country'}).find('span').string,
            'years_experience': tr.find(attrs={'data-stat': 'years_experience'}).string,
            'college_name': tr.find(attrs={'data-stat': 'college_name'}).string,
            'uri': _a['href'],
        }
        ps.append(p)
        print(p)
    return ps


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('please input the year. example: 2016 represent the season of 2015-2016')
        exit()
    if 2002 > int(sys.argv[1]) or int(sys.argv[1]) > 2016:
        print('the year must in 2013-2016')
        exit()

    players = []

    path = '%s/teams/teams.csv' % os.path.dirname(sys.path[0])
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            print(row['short_name'])
            players_team = crawl_players(row['%s_short' % sys.argv[1]], row['name'], sys.argv[1])
            players.extend(players_team)

    path = '%s/players_%s.csv' % (sys.path[0], sys.argv[1])
    with open(path, 'w', newline='') as csvfile:
        fieldnames = ['name', 'team', 'short_team', 'number', 'pos', 'height', 'weight', 'birth_date',
                      'birth_country', 'years_experience', 'college_name', 'uri']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(players)
