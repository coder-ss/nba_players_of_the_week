NBA 周最佳球员预测

## 数据获取

`./data`目录是数据目录

### 抓取原始数据

1. 通过`./data/teams/teams.py`抓取球队信息
2. 通过`./data/players/players.py 2016`抓取某个赛季的球员信息，参数2016表示2015-16赛季
3. 通过`./data/gamelogs/gamelogs.py 2016`抓取某个赛季每个球员每场比赛的数据，参数2016表示2015-16赛季
4. 通过`./data/players_of_week/pows.py`抓取周最佳球员
5. 通过`./dta/win_pct/win_pct.py 2016`组织每个赛季每个球队在每个阶段的胜率，参数2016表示2015-16赛季
6. 通过`./data/train/train.py 2016`组织用于训练的数据

其中

- `./data/teams/teams.py`、`./data/players/players.py 2016`、`./data/player_of_week/pows.py`每次执行都会覆盖原文件。
- `./data/gamelogs/gamelogs.py 2016`则每次在原文件的基础上追加写入，当某个球员的数据抓取过以后不会再抓取，可以反复执行，好处是就算某次抓取因为异常中断了，或者某个球员抓失败了，可以直接补抓。
- `./data/teams/teams_area.csv`是我人工标记的数据，标记球队属于东部还是西部

文件夹中的csv文件是已经抓好的数据，可以直接使用。

### 数据组织

运行脚本`./data/train/train_data.py 2016`，参数2016表示2015-16赛季。得到`./data/train/`文件夹中的csv文件，每一个文件是一周的球员数据，如果是周最佳，则用is_pow=1来标记。

data_2015-03-02中Isaiah Thomas由于交易出现在了两支球队中，两次都标记成了周最佳，人工将PHO的那条记录的is_pow标记为0。


## 预测

`./train/logistic_regression.py` 通过逻辑回归预测。效果不是很理想，能正确预测周最佳球员的概率是43%，能在前两位预测出周最佳的概率是61%，能在前三位预测出周最佳的概率是72%。