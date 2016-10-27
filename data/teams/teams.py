import requests
from bs4 import BeautifulSoup
import csv
import sys


def get_short_by_year(short_name):
    _url = 'http://www.basketball-reference.com/teams/%s/' % short_name
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

    d = {}
    d['2013_short'] = soup.find('a', text='2012-13')['href'].replace('/teams/', '').replace('/2013.html', '')
    d['2014_short'] = soup.find('a', text='2013-14')['href'].replace('/teams/', '').replace('/2014.html', '')
    d['2015_short'] = soup.find('a', text='2014-15')['href'].replace('/teams/', '').replace('/2015.html', '')
    d['2016_short'] = soup.find('a', text='2015-16')['href'].replace('/teams/', '').replace('/2016.html', '')

    return d

def crawl_team():
    _url = 'http://www.basketball-reference.com/teams/'
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

    tbody = soup.find(attrs={'id':'teams_active'})

    trs = tbody.find_all("tr", attrs={'class':'full_table'})

    teams = []
    for tr in trs:
        _a = tr.find("a")
        short_name = _a['href'].replace('teams', '').replace('/', '')
        t = {
            'name':_a.string,
            'short_name':short_name,
            'league': tr.find(attrs={'data-stat':'lg_id'}).string,
            'from': tr.find(attrs={'data-stat': 'year_min'}).string,
            'to': tr.find(attrs={'data-stat': 'year_max'}).string,
            'years': tr.find(attrs={'data-stat': 'years'}).string,
            'games': tr.find(attrs={'data-stat': 'g'}).string,
            'wins': tr.find(attrs={'data-stat': 'wins'}).string,
            'losses': tr.find(attrs={'data-stat': 'losses'}).string,
            'win_loss_pct': tr.find(attrs={'data-stat': 'win_loss_pct'}).string,
            'years_playoffs': tr.find(attrs={'data-stat': 'years_playoffs'}).string,
            'years_division_champion': tr.find(attrs={'data-stat': 'years_division_champion'}).string,
            'years_conference_champion': tr.find(attrs={'data-stat': 'years_conference_champion'}).string,
            'years_league_champion': tr.find(attrs={'data-stat': 'years_league_champion'}).string
        }
        shorts = get_short_by_year(short_name)
        for k in shorts:
            t[k] = shorts[k]

        teams.append(t)

    path = '%s/teams.csv' % sys.path[0]
    with open(path, 'w', newline='') as csvfile:
        fieldnames = ['short_name', 'name', 'league', 'from', 'to', 'years', 'games', 'wins',
                      'losses','win_loss_pct','years_playoffs','years_division_champion',
                      'years_conference_champion', 'years_league_champion',
                      '2013_short', '2014_short', '2015_short', '2016_short']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(teams)


if __name__ == '__main__':
    crawl_team()
