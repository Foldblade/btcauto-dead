# encoding:utf-8

import datetime
import pandas
import json
import requests
import os
import time
import threading
import api
import quickmail

where_script = os.path.split(os.path.realpath(__file__))[0]

now = datetime.datetime.now()
now.strftime('%Y-%m-%d %H:%M:%S')
nowtime = now.strftime('%Y-%m-%d %H:%M:%S')
print(nowtime)

print('Start at ' + time.ctime())

coins = ['btc', 'eth', 'etc', 'ltc', 'doge', 'ybc']

f = open(where_script + '/data/pricenow.json', 'r')
pricedata = json.load(f)
f.close()

f = open(where_script + '/setting.json', 'r')
setting_json = json.load(f)
f.close()

f = open(where_script + '/data/tradenow.json', 'r')
tradenow_json = json.load(f)
f.close()

pricedata['time'] = nowtime
# 用来存储获得的当前价格，参考json文件吧。
# 当前价格coin + last、上一次价格coin + previous、当前买一价coin + buy、当前卖一价coin + sell、上一买一价coin + pre_buy、上一卖一价coin + pre_sell、当前交易量coin + vol 、上一交易量coin + pre_vol
# 下面一个函数用来填充pricedata

previousdata = pandas.read_csv(where_script + '/data/pricelog_min.csv')
finlinedata = previousdata.iloc[-1, ]




def priceget(coin):

    pricedata[coin]['previous'] = float(finlinedata[coin])
    pricedata[coin]['pre_buy'] = float(finlinedata[coin + '_buy'])
    pricedata[coin]['pre_sell'] = float(finlinedata[coin + '_sell'])
    pricedata[coin]['pre_vol'] = int(finlinedata[coin + '_vol'])
    # 处理上一数据，转移、记录
    try:
        print(coin.upper() + ':connecting……' + time.ctime())
        url = 'https://api.btctrade.com/api/ticker?coin=' + coin
        response = requests.get(url, timeout=5).text
        # 抓取比特币价格网页
        js_dict = json.loads(response)
        print(coin + ' price:' + str(js_dict['last']))
        print(coin + ' sell:' + str(js_dict['sell']))
        print(coin + ' buy:' + str(js_dict['buy']))
        pricedata[coin]['price'] = js_dict['last']
        pricedata[coin]['buy'] = js_dict['buy']
        pricedata[coin]['sell'] = js_dict['sell']
        pricedata[coin]['vol'] = js_dict['vol']
        pricedata[coin]['trend'] = round(pricedata[coin]['price'] - pricedata[coin]['previous'], 5)
        print(coin.upper() + ' get done at ' + time.ctime())

        tradenow_json['time'] = nowtime

        if setting_json[coin]['trade'] == 1:
            fee = 0.002
            '''根据9月8日抑制投机公告，全都是0.2%了。
            if coin == 'btc' or 'ltc': # 手续费
                fee = 0.002
            elif coin == 'ybc' or 'doge' or 'etc':
                fee = 0.001
            elif coin == 'eth':
                fee = 0.0005
            '''
            def process_trade_confirm(coin):
                print('卖出交易正在确认。')
                try:
                    fetch_sell_return = api.fetch_order(tradenow_json[coin]['sell_id'])
                except:
                    print('|CON-ERROR|>>>交易确认失败。')

                if fetch_sell_return["status"] == "closed":
                    print('我们买了的虚拟币卖出去了。We sold some coins.')
                    buy_id = int(tradenow_json[coin]['buy_id'])
                    sell_id = int(tradenow_json[coin]['sell_id'])
                    try:
                        info_json = api.info()
                        quickmail.mail(coin.upper() + '卖出交易报告',
                                       '程序于' + nowtime + '自动进行了一笔交易。\r\n' +
                                       '买入单号:' + str(buy_id) + '\r\n' +
                                       '卖出单号:' + str(sell_id) + '\r\n' +
                                       '卖出前资产(RMB):' + str(tradenow_json[coin]["last_asset"]) + '\r\n' +
                                       '现资产(RMB): %(asset)s' % info_json + '\r\n'+
                                       '————————————————————\r\n' +
                                       coin.upper() + '余额:' + str(info_json[coin + '_balance']) + '\r\n'+
                                       coin.upper() + '冻结:' + str(info_json[coin + '_reserved'])+ '\r\n' +
                                       '人民币余额: %(cny_balance)s \r\n' % info_json +
                                       '人民币冻结: %(cny_reserved)s \r\n' % info_json
                                       )
                    except:
                        pass
                    tradenow_json[coin]['type'] = 'buy'
                    tradenow_json[coin]['amount'] = 0
                    tradenow_json[coin]['buy_id'] = 0
                    tradenow_json[coin]['sell_id'] = 0
                    tradenow_json[coin]['buy_price'] = 0
                    tradenow_json[coin]['sell_price'] = 0
                    tradenow_json[coin]['last_asset'] = 0
                    print('数据初始化完毕。The data was initialized.')
                return

            def process_sell(coin):
                print('正在重做失败的挂单卖出操作。')
                buy_id = int(tradenow_json[coin]['buy_id'])
                try:
                    fetch_buy_return = api.fetch_order(buy_id)
                    print(fetch_buy_return)
                    if fetch_buy_return['status'] == 'closed':
                        print('买单交易结束。')
                        sum_number = fetch_buy_return['trades']['sum_number']
                        avg_price = fetch_buy_return['trades']['avg_price']
                        sum_money = fetch_buy_return['trades']['sum_money']
                        amount_orginal = fetch_buy_return['amount_original']
                        # price_original = amount_orginal = fetch_buy_return['price'] # 请求卖出价格
                        tradenow_json[coin]['buy_price'] = avg_price  # 记录买入价格
                        tradenow_json[coin]['amount'] = amount_orginal  # 记录买入数量
                        sell_fee = sum_money * fee
                        expect_value = sum_money + (sell_fee * 2) + setting_json[coin]['income']
                        expect_price = expect_value / sum_number
                        try:
                            sell_return = api.sell_order(coin, amount_orginal, expect_price)
                            print(sell_return)
                            if sell_return['result'] is False:
                                print('||RE:ERROR|>>>计划卖单确认失败。')
                                tradenow_json[coin]['type'] = 'sell'
                                try:
                                    quickmail.mail('比特币自动交易-失败提示', nowtime +
                                                   'RE:ERROR：计划卖出交易失败。' +
                                                   sell_return['message'] +
                                                   '程序已经在尝试进行自我挽救。')
                                except:
                                    pass
                                # 补救措施
                                info_json = api.info()
                                amount_orginal = info_json[coin + '_balance']
                                sell_return = api.sell_order(coin, amount_orginal, expect_price)
                                print(sell_return)
                                if sell_return['result'] is False:
                                    print('||RE:ERROR|>>>计划卖单确认失败。')
                                    tradenow_json[coin]['type'] = 'sell'
                                    try:
                                        quickmail.mail('比特币自动交易-失败提示', nowtime +
                                                       'RE:ERROR：计划卖出交易失败。补救措施失败。' +
                                                       sell_return['message'] +
                                                       '请速上线进行处理！')
                                    except:
                                        pass
                                else:
                                    tradenow_json[coin]['type'] = 'trade_confirm'
                                    sell_id = int(sell_return['id'])
                                    tradenow_json[coin]['sell_id'] = sell_id
                                    fetch_sell_return = api.fetch_order(sell_id)
                                    tradenow_json[coin]['sell_price'] = expect_price
                                    print('补救后计划卖单成功。')
                            else:
                                tradenow_json[coin]['type'] = 'trade_confirm'
                                sell_id = int(sell_return['id'])
                                tradenow_json[coin]['sell_id'] = sell_id
                                fetch_sell_return = api.fetch_order(sell_id)
                                tradenow_json[coin]['sell_price'] = expect_price
                                print('计划卖单成功。')
                                pass
                        except:
                            print('|ERROR|>>>计划卖出交易失败。')
                            try:
                                quickmail.mail('比特币自动交易-失败提示', nowtime +
                                               '计划卖出交易失败。')
                            except:
                                pass
                    else:
                        print('买单尚未结束，未进行卖出操作。')
                except:
                    print('|ERROR|>>>交易失败。可能需要debug。')
                    try:
                        quickmail.mail('DEBUG失败提示', nowtime +
                                       '交易失败。')
                    except:
                        pass

                try:
                    quickmail.mail(coin.upper() + '买入交易报告',
                                   '程序于' + nowtime + '自动进行了一笔交易。\r\n' +
                                   '买入前折合总资产(RMB):' + str(tradenow_json[coin]['last_asset']) + '\r\n' +
                                   '买入单号:' + str(buy_id) + '\r\n' +
                                   '卖出单号:' + str(sell_id) + '\r\n' +
                                   '买入' + coin.upper() + '总价值（RMB）:' + str(sum_money) + '\r\n' +
                                   '买入' + coin.upper() + '价格:' + str(avg_price) + '\r\n' +
                                   '买入' + coin.upper() + '数目:' + str(amount_orginal) + '\r\n' +
                                   '期待售价:' + str(expect_price) + '\r\n'
                                   )
                    print('交易提示邮件发送成功。')
                except:
                    pass

                print('我们买了点虚拟币。We brought some coins.')
                return

            def process_buy(coin):
                try:
                    info_json = api.info()
                except:
                    print('获取账户信息失败')

                tradenow_json[coin]['last_asset'] = info_json['asset']
                # 刷新资产

                maxlimit = float(setting_json[coin]['max'])
                if maxlimit > float(info_json['cny_balance']):
                    trade_rmb = float(info_json['cny_balance'])  # 对最大交易量的判断。
                    try:
                        quickmail.mail('比特币自动交易-提示', nowtime +
                                       '\r\n您的账户里人民币余额小于您设置的最大交易量。全部人民币已经用于本次交易。')
                    except:
                        pass
                else:
                    trade_rmb = maxlimit  # 用来买的RMB数目

                coin_amount = trade_rmb / pricedata[coin]['price']
                coin_amount = float(str(coin_amount)[:str(coin_amount).find('.') + 3])  # 可以买到的虚拟币数目
                print('CNY to ' + coin + ' : ' + str(coin_amount))

                if maxlimit <= 0:
                    pass
                else:
                    buy_in = float(coin_amount)  # 买入的虚拟币数目

                    try:
                        buy_return = api.buy_order(coin, buy_in, pricedata[coin]['buy'])# * 1.001)
                        print(buy_return)
                        # 为什么* 1.001？用交易网的自动匹配，加速交易流程。
                        # 在测试中我们发现了一些问题。可能有时交易网不会自动匹配，造成了一定的亏损。那么还是注释掉吧？
                        if buy_return['result'] is False:
                            print('||RE:ERROR|>>>买入交易失败。')
                            tradenow_json[coin]['type'] = 'buy'
                        else:
                            buy_id = int(buy_return['id'])
                            print(buy_return['id'])
                            tradenow_json[coin]['type'] = 'sell'
                            tradenow_json[coin]['buy_id'] = buy_id
                    except:
                        print('|ERROR|>>>买入交易失败。')
                        pass

                    try:
                        time.sleep(0.5)
                        fetch_buy_return = api.fetch_order(buy_id)
                        print(fetch_buy_return)
                        if fetch_buy_return['status'] == 'closed':
                            print('买单交易结束。')
                            sum_number = fetch_buy_return['trades']['sum_number']
                            avg_price = fetch_buy_return['trades']['avg_price']
                            sum_money = fetch_buy_return['trades']['sum_money']
                            amount_orginal = fetch_buy_return['amount_original']
                            # price_original = amount_orginal = fetch_buy_return['price'] # 请求卖出价格
                            tradenow_json[coin]['buy_price'] = avg_price  # 记录买入价格
                            tradenow_json[coin]['amount'] = amount_orginal  # 记录买入数量
                            sell_fee = sum_money * fee
                            expect_value = sum_money + (sell_fee * 2) + setting_json[coin]['income']
                            expect_price = expect_value / sum_number
                            try:
                                time.sleep(0.5)
                                sell_return = api.sell_order(coin, amount_orginal, expect_price)
                                print(sell_return)
                                if sell_return['result'] is False:
                                    print('||RE:ERROR|>>>计划卖单确认失败。')
                                    tradenow_json[coin]['type'] = 'sell'
                                    try:
                                        quickmail.mail('比特币自动交易-失败提示', nowtime +
                                                       'RE:ERROR：计划卖出交易失败。' +
                                                       sell_return['message'] +
                                                       '程序已经在尝试进行自我挽救。')
                                    except:
                                        pass
                                    # 补救措施
                                    info_json = api.info()
                                    amount_orginal = info_json[coin + '_balance']
                                    sell_return = api.sell_order(coin, amount_orginal, expect_price)
                                    print(sell_return)
                                    if sell_return['result'] is False:
                                        print('||RE:ERROR|>>>计划卖单确认失败。')
                                        tradenow_json[coin]['type'] = 'sell'
                                        try:
                                            quickmail.mail('比特币自动交易-失败提示', nowtime +
                                                           'RE:ERROR：计划卖出交易失败。补救措施失败。' +
                                                           sell_return['message'] +
                                                           '请速上线进行处理！')
                                        except:
                                            pass
                                    else:
                                        tradenow_json[coin]['type'] = 'trade_confirm'
                                        sell_id = int(sell_return['id'])
                                        tradenow_json[coin]['sell_id'] = sell_id
                                        fetch_sell_return = api.fetch_order(sell_id)
                                        tradenow_json[coin]['sell_price'] = expect_price
                                        print('补救后计划卖单成功。')
                                else:
                                    tradenow_json[coin]['type'] = 'trade_confirm'
                                    sell_id = int(sell_return['id'])
                                    tradenow_json[coin]['sell_id'] = sell_id
                                    fetch_sell_return = api.fetch_order(sell_id)
                                    tradenow_json[coin]['sell_price'] = expect_price
                                    print('计划卖单成功。')
                                    pass
                            except:
                                print('|ERROR|>>>计划卖出交易失败。')
                                try:
                                    quickmail.mail('比特币自动交易-失败提示', nowtime +
                                                   '计划卖出交易失败。')
                                except:
                                    pass
                        else:
                            print('买单尚未结束，未进行卖出操作。')
                    except:
                        print('|ERROR|>>>交易失败。可能需要debug。')
                        try:
                            quickmail.mail('DEBUG失败提示', nowtime +
                                           '交易失败。')
                        except:
                            pass

                    try:
                        quickmail.mail(coin.upper() + '买入交易报告',
                                       '程序于' + nowtime + '自动进行了一笔交易。\r\n' +
                                       '买入前折合总资产(RMB):' + str(tradenow_json[coin]['last_asset']) + '\r\n' +
                                       '买入单号:' + str(buy_id) + '\r\n' +
                                       '卖出单号:' + str(sell_id) + '\r\n' +
                                       '买入' + coin.upper() + '总价值（RMB）:' + str(sum_money) + '\r\n' +
                                       '买入' + coin.upper() + '价格:' + str(avg_price) + '\r\n' +
                                       '买入' + coin.upper() + '数目:' + str(amount_orginal) + '\r\n' +
                                       '期待售价:' + str(expect_price) + '\r\n'
                                       )
                        print('交易提示邮件发送成功。')
                    except:
                        pass

                    print('我们买了点虚拟币。We brought some coins.')
                return

            if tradenow_json[coin]['type'] == 'trade_confirm':
                process_trade_confirm(coin)

            elif tradenow_json[coin]['type'] == 'sell':
                process_sell(coin)

            else:# 购买流程
                buy_log = previousdata[coin + '_buy']
                lowest_buy = min(buy_log[-240:])
                if lowest_buy >= pricedata[coin]['buy']:
                    print('现在是最近4h的最低价。It is the lowest of last 4h.')

                    print(tradenow_json[coin]['type'])
                    if tradenow_json[coin]['type'] == 'buy':
                        print('判断为空仓。可以买入。We can buy in.')

                        # 下面是规则段。优化这里来提升自动交易姿势水平。
                        Sum = sum(buy_log)
                        Average = Sum / len(buy_log)
                        if pricedata[coin]['buy'] < Average:
                            process_buy(coin)

                        # 以上是规则段。如果注释掉是按四小时最小值+设定期望进行自动交易。

                    else:
                        print('不是空仓，不买。Oh no, we cannot buy in.')
                else:
                    print('并不是最近4h的最低价。It is NOT the lowest of last 4h.')




    except:
        print('|CON-ERROR|>>>' + coin.upper() + ' connecting fail at ' + time.ctime())
        pricedata[coin]['price'] = pricedata[coin]['previous']
        pricedata[coin]['buy'] = pricedata[coin]['pre_buy']
        pricedata[coin]['sell'] = pricedata[coin]['pre_sell']
        pricedata[coin]['sell'] = pricedata[coin]['pre_vol']
        pricedata[coin]['trend'] = round(pricedata[coin]['price'] - pricedata[coin]['previous'], 5)
        print('|CON-ERROR|>>>' + coin.upper() + ' load previous log at ' + time.ctime())

    return pricedata

count = range(len(coins))
threads = []
for coin in coins:
    t = threading.Thread(target=priceget,args=(coin,))
    threads.append(t)

if __name__ == '__main__':
    for i in count:
        threads[i].start()
    for i in count:
        threads[i].join()

    print("|M.P.|>>>All over at " + time.ctime())

data = pandas.read_csv(where_script + '/data/pricelog_min.csv')
data = data.drop(0)
data.to_csv(where_script + '/data/pricelog_min.csv', sep=",", index=False)
#删价格首行

f = open(where_script + '/data/pricelog_min.csv','a+')
data = nowtime
for coin in coins:
    data = data + ',' + str(pricedata[coin]['price']) + ',' + str(pricedata[coin]['trend']) +  ',' + str(pricedata[coin]['buy']) + ',' + str(pricedata[coin]['sell']) + ',' + str(pricedata[coin]['vol'])
f.write(data)
f.close()

f = open(where_script + '/data/pricelog_all.csv','a+')
data = nowtime
for coin in coins:
    data = data + ',' + str(pricedata[coin]['price']) + ',' + str(pricedata[coin]['trend']) +  ',' + str(pricedata[coin]['buy']) + ',' + str(pricedata[coin]['sell']) + ',' + str(pricedata[coin]['vol'])
data = data + '\n'
f.write(data)
f.close()

f = open(where_script + '/data/pricenow.json', 'w')
json.dump(pricedata, f, indent=4)
f.close()
#记录价格

f = open(where_script + '/data/tradenow.json', 'w')
json.dump(tradenow_json, f, indent=4)
f.close()


print('record done!')
