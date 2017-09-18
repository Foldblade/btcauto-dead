# encoding:utf-8

# import pandas
import csv
import codecs
import matplotlib as mpl
# import numpy
mpl.use('Agg')
import matplotlib.pyplot as plt
import datetime
# from matplotlib.ticker import MultipleLocator
# import matplotlib.dates as mdate
import os
import json
import shutil

where_script = os.path.split(os.path.realpath(__file__))[0]


now = datetime.datetime.now()
now.strftime('%Y-%m-%d %H:%M')
nowtime = now.strftime('%Y-%m-%d %H:%M')
print(nowtime)

coins = ['btc', 'eth', 'etc', 'ltc', 'doge', 'ybc']
f = codecs.open(where_script + '/setting.json', 'r', 'utf-8')
setting = json.load(f)
f.close()

to_draw = []
for coin in coins:
    if int(setting[str(coin)]['draw']) != 0:
        to_draw.append(coin)
    else:
        pass
print('To draw:' + str(to_draw))

'''
Bug 写法，不知道为什么。
for coin in coins:
    if int(setting[str(coin)]['draw']) == 0:
        print(coin + ' need\'t to be drawn.')
        coins.remove(coin)
    else:
        print(coin + ' need to be drawn.')

print(str(coins))
# 错误的输出：['btc', 'eth', 'etc', 'ltc', 'ybc'] 我只设定了前4个的draw = 1
'''

def  pricelog(coin):
    global date, pricelist, vollist, average, length, sum

    with open("data/pricelog_min.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        date = [row['time'] for row in reader]
        # print(len(date))
        csvfile.close()

    with open("data/pricelog_min.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        pricelist = [row[ str(coin) ] for row in reader]
        pricelist = list(map(eval, pricelist))
        # print(pricelist)
        # print(len(pricelist))
        csvfile.close()

    with open("data/pricelog_min.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        vollist = [row[str(coin)+'_vol'] for row in reader]
        vollist = list(map(eval, vollist))
        # print(vollist)
        # print(len(vollist))
        csvfile.close()

    Sum = sum(pricelist)
    # print(Sum)
    average = Sum / len(pricelist)
    average = round(average, 3)
    # print('average =', average)
    # 求平均值
    return


def draw(coin):
    fig = plt.figure(figsize=(21, 9), dpi=200)
    pricelog(coin)
    ax1 = fig.add_subplot(111)
    ax1.set_xticks(range(0,len(date),20))
    ax1.set_xticklabels([datetime.datetime.strptime(date[i], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')  # 设置时间标签显示格式
                         for i in range(0,len(date),20)])  # 时间间隔
    plt.xticks(rotation=90, fontsize=8)
    ax1.set_xlabel('Time (freq=20min)', size=15)
    ax1.set_ylabel('Price/¥', size=15)
    ax1.set_title(coin.upper() + ' Price Daily' + '\n' + nowtime, size=20)
    ax1.plot(range(len(date)), pricelist, linewidth=1.0, label='Price')
    ax1.plot(range(len(date)), [average for obj in date], linewidth=1.0, linestyle='-.',label='Average')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(range(len(date)), vollist, linewidth=1.0, color='g', linestyle='--', alpha=0.3,label='Vol')
    ax2.fill_between(range(len(date)), vollist, [min(vollist) for vol in vollist], color='g', alpha=0.25)
    # ax2.bar(range(len(vollist)), [float(vol) for vol in vollist], [1 for vol in vollist], [0 for vol in vollist],color='g', alpha=0.25) 柱状图版本。还不如fill。
    ax2.set_ylabel('Vol of 24h', size=15)
    ax2.legend(loc='upper right')
    # ax2.grid(True)
    plt.subplots_adjust(wspace=20,hspace=20)
    plt.savefig(where_script + '/data/'+ coin + '.png', dpi=150)

    print('PNG saved!')
    return()


for coin in to_draw:
    draw(coin)
    #if setting['web'] == 1:
    #    shutil.copy(where_script + '/data/' + coin + '.png', where_script + '/public/' + coin + '.png')
    #    print('Copied!')
