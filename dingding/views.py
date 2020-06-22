#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# __author__ = 'bigc'
# @Time    : 2020/4/12 21:44
# views部分代码

from django.http import HttpResponse, JsonResponse
import json, re,paramiko
from chatops.settings import *
import hmac
import hashlib
import base64, requests
from django.core.cache import cache
from . import shell,zabbix,jenkins
from jira import JIRA

# 机器人的app_secret
app_secret = "fkyymqRK_Jr-nmKX4tk9ogMn9OmT87HeDmeJC6Gt30JeRwLQcR94PEf_UwX0EiKi"
zabbix_url = ZABBIX_URL
zabbix_user = ZABBIX_USER
zabbix_password = ZABBIX_PASSWORD
headers = {"Content-Type": "application/json"}
# 定义全局认证信息
auth = ''
jira = ''

class jira:
    def __init__(self):
        pass
    #     self.options = {"server": "http://60.205.177.168:500"}
    #     self.jira = JIRA(basic_auth=("admin", "asd123456"), options=self.options)
    #
    # def getjiraitem(self):
    #     projects = self.jira.projects()
    #     return str(projects)

jiras = {'获取jira项目': 'getjiraitem'}
jira = jira()


class help:
    def help(self):
        self.menu = """## 帮助信息 \n ————————————\n ### 1、zabbix \n - 获取zabbix的所有用户 \n - 获取zabbix的版本信息 \n - 获取zabbix[IP]的主机信息 \n - 获取zabbix[IP]的报警信息 \n - 获取zabbix[IP]的事件信息 \n - 获取zabbix[IP]的巡检表 \n ### 2、处理Kubernetes\n ### 3、执行Linux命令 \n - shell 内存信息[IP] \n - shell 磁盘信息[IP]\n - shell 端口检测 [IP|DOMAIN]:[PORT] \n - shell 日志信息 [IP] [LOGPATH] \n - shell 负载信息 [IP] \n - shell 服务检测 [IP][DOMAIN] - shell 重启服务[IP][service]\n ### 4、处理Jenkins \n - 查询jenkins的所有job \n - 查询jenkins的所有视图 \n - 查询jenkins视图[view_name]下的所有job \n - 构建jenkins build [job_name] \n - 重启jenkins  \n  ——————————————  \n   请按着帮助信息输入内容！"""
        return self.menu


help = help()

def robot(request):
    if request.method == "POST":
        HTTP_SIGN = request.META.get("HTTP_SIGN")
        HTTP_TIMESTAMP = request.META.get("HTTP_TIMESTAMP")
        res = json.loads(request.body)
        print(res)
        # print(zabbix_url)
        # 用户输入钉钉的信息
        content = res.get("text").get("content").strip()
        # print(content)
        string_to_sign = '{}\n{}'.format(HTTP_TIMESTAMP, app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret.encode("utf-8"), string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        # print(sign)
        # print(HTTP_SIGN)
        # 验证签名是否为钉钉服务器发来的
        sendnick = json.loads(request.body)['senderNick']
        print(sendnick)
        getname = cache.get('name')
        getdata = cache.get('data')

        if getname == sendnick and getdata != None:
            content = getdata + "|" + content
            print(getname)
        else:
            cache.delete("data")
            cache.set("name", sendnick)
            print(getname)
        if sign == HTTP_SIGN:

            if content == 'help':
                rest = getattr(help, content)
                print(rest())
                return JsonResponse(
                    {"msgtype": "markdown",
                        "markdown": {
                            "title": 'help',
                            "text": rest()
                        },
                     }
                )
            if 'shell' in content:
                shells=shell.shellres(content)
                return shells
            if 'zabbix' in content:
                zabbixs=zabbix.zabbixres(content)
                return zabbixs
            if 'jenkins' in content:
                pass


            return JsonResponse(
                {"msgtype": "text",
                 "text": {
                     "content": "谢谢使用此机器人，{}".format(content)
                 }
                 }
            )
        return JsonResponse({"error": "你没有权限访问此接口"})
    if request.method == "GET":
        return HttpResponse("hello")
