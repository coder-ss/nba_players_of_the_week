NBA 周最佳球员预测

## 数据获取

`./data`目录是数据目录

### 抓取原始数据

1. 通过`./data/teams/teams.py`抓取球队信息
2. 通过`./data/players/players.py 2016`抓取某个赛季的球员信息，参数2016表示2015-16赛季
3. 通过`./data/gamelogs/gamelogs.py 2016`抓取某个赛季每个球员每场比赛的数据，参数2016表示2015-16赛季
4. 通过`./data/players_of_week/pows.py`抓取周最佳球员

其中

- `./data/teams/teams.py`、`./data/players/players.py 2016`、`./data/player_of_week/pows.py`每次执行都会覆盖原文件。
- `./data/gamelogs/gamelogs.py 2016`则每次在原文件的基础上追加写入，当某个球员的数据抓取过以后不会再抓取，可以反复执行，好处是就算某次抓取因为异常中断了，或者某个球员抓失败了，可以直接补抓。

文件夹中的csv文件是已经抓好的数据，可以直接使用。

### 数据组织

## 预测