import requests
from bs4 import BeautifulSoup
import csv
import sys
import os
import time
import datetime


def format_date(season, mon, day):
    arr = season.split('-')
    season_start_year = int(arr[0])

    time_format = datetime.datetime.strptime(mon, '%B')
    m = time_format.strftime('%m')
    if int(m) > 9:
        y = season_start_year
    else:
        y = season_start_year + 1

    time_format = datetime.datetime.strptime('%s %s' % (y,day), '%Y %b %d')

    format_day = time_format.strftime('%Y-%m-%d')
    return format_day


def crawl_pow():
    _url = 'http://www.basketball-reference.com/awards/pow.html'
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

    div = soup.find('div', id='all_')
    h3s = div.find_all('h3')

    rs = {}
    for h3 in h3s:
        season = h3.string
        print(season)
        months = h3.parent.find_all('div', attrs={'class':'data_grid_box'})

        for m in months:
            key = m.find('div', attrs={'class':'gridtitle'}).string  # November
            # print(key)
            ps = m.find_all('p')
            for p in ps:
                obj_d = p.find('strong')
                if obj_d is not None:
                    d = obj_d.string
                    try:
                        # print(d)
                        pow_e = p.find('a', attrs={'data-desc':'%s Eastern' % key})
                        # print(pow_e)
                        pow_w = p.find('a', attrs={'data-desc': '%s Western' % key})
                        # print(pow_w)
                    except Exception as e:
                        continue

                    if pow_e is not None and pow_w is not None:
                        format_d = format_date(season, key, d)
                        rs['%s_eastern' % format_d] = {
                            'date': format_d,
                            'area': 'eastern',
                            'name': pow_e.string,
                            'uri': pow_e['href'],
                        }
                        rs['%s_western' % format_d] = {
                            'date': format_d,
                            'area': 'western',
                            'name': pow_w.string,
                            'uri': pow_w['href'],
                        }

    return [rs[k] for k in sorted(rs.keys(), reverse=True)]


if __name__ == '__main__':
    pows = crawl_pow()

    path = '%s/pows.csv' % sys.path[0]
    with open(path, 'w', newline='') as csvfile:
        fieldnames = ['date', 'area', 'name', 'uri']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(pows)
