# encoding:utf-8
import os
import smtplib  #加载smtplib模块
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import mimetypes
import json

where_script = os.path.split(os.path.realpath(__file__))[0]

f = open(where_script + '/.mailsetting.json', 'r')
mailjson = json.load(f)
f.close()

def mail(mail_title,mail_body):
    receivers = mailjson["receivers"]
    for people in receivers:
        print(people)
        message = MIMEMultipart()

        # 第三方 SMTP 服务
        smtp_host = mailjson["smtp_host"]  # SMTP服务器
        smtp_port = mailjson["smtp_port"]
        smtp_user = mailjson["smtp_user"]  # 用户名
        smtp_passwd = mailjson["smtp_passwd"]  # 密码

        sender = mailjson["sender"]  # 发件人邮箱(最好写全, 不然会失败)
        receiver = [people]
        print(receiver)

        title = str(mail_title)  # 邮件主题
        message.attach(MIMEText(mail_body, 'plain', 'utf-8'))  # 内容, 格式, 编码

        message['From'] = "{}".format(sender)
        message['To'] = ",".join(receiver)
        message['Subject'] = title

        '''
        coins = ['btc', 'eth', 'etc', 'ltc', 'doge', 'ybc']
        f = open(where_script + '/setting.json', 'r')
        setting = json.load(f)
        f.close()

        to_mail_coins = []
        for coin in coins:
            if int(setting[str(coin)]['mail']) != 0:
                to_mail_coins.append(coin)
            else:
                pass
        print('To mail:' + str(to_mail_coins))
        coins = to_mail_coins

        file_names = []
        for coin in coins:
            file_names.append(where_script + '/data/' + coin + '.png')
        for file_name in file_names:
            data = open(file_name, 'rb')
            ctype, encoding = mimetypes.guess_type(file_name)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            file_msg = MIMEBase(maintype, subtype)
            file_msg.set_payload(data.read())
            data.close()
            encoders.encode_base64(file_msg)  # 把附件编码
            basename = os.path.basename(file_name)
            file_msg.add_header('Content-Disposition', 'attachment', filename=basename)# 修改邮件头
            message.attach(file_msg)  # 设置根容器属性
            '''

        try:
            smtpObj = smtplib.SMTP_SSL(smtp_host, smtp_port)  # 启用SSL发信, 端口一般是465
            smtpObj.login(smtp_user, smtp_passwd)  # 登录验证
            smtpObj.sendmail(sender, receiver, message.as_string())  # 发送
            print(people + "'s mail has been send successfully.")
        except smtplib.SMTPException as e:
            print(e)
    return
