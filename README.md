# BTCauto-dead
API 和 交易平台 使用 [比特币交易网](https://www.btctrade.com).（已死）  
比特币交易网即将于2017年9月30日前停止所有交易。
说是“自动交易”……其实就是调用API。


## 本人环境：  
`Python 3.5.3`  
`CentOS 6.6`  
**~~建议将系统调为中文环境，某些输出可能涉及中文~~**

## 已经实现的功能：
- BTC、ETH、ETC、LTC、DOGE、YBC的支持
- 邮件发送
- 汇报平均值、方差、极差、最大最小值
- 绘制24小时内比特币价格折线图
- 自动交易

## 具体配置：
主要分为以下两个部分：
- 数据抓取部分
- 邮件发送部分

**使用前请在mailsetting.json内配置好邮件服务器和接收邮箱！！！**  
日后会加入数据分析……  
数据抓取部分，每分钟从交易网站抓取价格，并以csv格式记录。  
在Linux上，我用crontab来每分钟执行一次main.py。   
然后依旧用crontab来定时，譬如每天21:00发送一次邮件，dailymail.py。

请注意：每次更新后，可能需要等待24小时来恢复正常状态。请耐心等待。

### 更新：
- 2017.9
  - 棒子下来了。一切都结束了。

- 2017.8
  - 试着写了自动交易。
  - 正在写一个Trade Panel方便管理。

- 2017.7.19
  - 新增对以太经典(ETC)的支持

- 2017.6.24
  - BTC、ETH、LTC、DOGE、YBC全支持。请在setting.json中配置（0即“不要”）
  - 更多的数据记录，为下一次升级铺垫
  - draw.py尝试加入交易量的绘制，更带来21：9的~~极差~~宽屏体验
  - 计划引用别人的一个api，LICENSE现为GPL 3.0

- 2017.5.29
  - 支持BTC、ETH、LTC记录、绘图
  - 邮件支持多附件，用HTML表格形式汇报
  - 邮件更注重隐私，为每个收件人单独发送邮件
  - 支持在 ‘mailsetting.json’中配置邮件服务和收件人

- 2017.4.4
  - 汇报平均值、方差、极差、最大最小值
  - 邮件附图加入平均值，x轴支持显示时间

enjoy ^_^
