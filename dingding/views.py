#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# __author__ = 'bigc'
# @Time    : 2020/4/12 21:44
# @Email   : luocs1@lenovo.com
# views部分代码

from django.http import HttpResponse, JsonResponse
import json, re
from chatops.settings import *
import hmac
import hashlib
import base64, requests
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


# Create your views here.
# 定义zabbix登陆注销的装饰器
def zabbix_loginout(func):
    def wrapper(*args):
        # print("wrapper args :", args)
        data = {"jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": zabbix_user,
                    "password": zabbix_password
                },
                "id": 1,
                "auth": None
                }
        global auth
        auth = requests.post(url=zabbix_url, headers=headers, json=data)
        auth = json.loads(auth.content)['result']
        # print("loginout auth:", auth)

        # temp = func(*args)
        temp = func()
        data = {
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": 1,
            "auth": auth
        }
        logout = requests.post(url=zabbix_url, headers=headers, json=data)
        # print("装饰器完成，exit")
        return temp

    return wrapper


class mapping:

    @staticmethod
    @zabbix_loginout
    def gethost():
        # print("gethost auth:", auth)
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend"
            },
            "auth": auth,
            "id": 1
        }
        # print("gethost data:", data)

        gethost = requests.post(url=zabbix_url, headers=headers, json=data)
        gethost = json.loads(gethost.content)['result']
        # print("gethost:", gethost)
        return gethost

    @staticmethod
    @zabbix_loginout
    def getalert():
        data = {
            "jsonrpc": "2.0",
            "method": "event.get",
            "params": {
                "output": "extend",
                "select_acknowledges": "extend",
                "selectTags": "extend",
                "sortfield": ["clock", "eventid"],
                "sortorder": "DESC"
            },
            "auth": auth,
            "id": 1
        }
        getalert = requests.post(url=zabbix_url, headers=headers, json=data)
        getalert = json.loads(getalert.content)['result']
        return getalert

    @staticmethod
    @zabbix_loginout
    def getzabbixuser():
        data = {
            "jsonrpc": "2.0",
            "method": "user.get",
            "params": {
                "output": [
                    "alias",
                    "name"
                ]
            },
            "auth": auth,
            "id": 1
        }
        getuser = requests.post(url=zabbix_url, headers=headers, json=data)
        getuser = json.loads(getuser.content)['result']
        return getuser


class jira:
    def __init__(self):
        self.options = {"server": "http://60.205.177.168:500"}
        self.jira = JIRA(basic_auth=("admin", "asd123456"), options=self.options)

    def getjiraitem(self):
        projects = self.jira.projects()
        return str(projects)


systems = {'获取60.205.177.168内存': 'getmeminfo'}
zabbixs = {'a': 'gethost', 'b': 'getalert', 'c': 'getzabbixuser'}
jiras = {'获取jira项目': 'getjiraitem'}
mapping = mapping()
jira = jira()


class help:
    def help(self):
        self.menu = """## 帮助信息 \n ————————————\n ### 1、zabbix \n - 获取zabbix的所有用户 \n - 获取zabbix的版本信息 \n - 获取zabbix[IP]的主机信息 \n - 获取zabbix[IP]的报警信息 \n - 获取zabbix[IP]的事件信息 \n - 获取zabbix[IP]的历史记录 \n ### 2、处理Kubernetes\n ### 3、执行Linux命令 \n - 获取[IP]的内存信息 \n - 获取[IP]的磁盘信息\n ### 4、处理Jenkins \n - 查询jenkins的所有job \n - 查询jenkins的所有视图 \n - 查询jenkins视图[view_name]下的所有job \n - 执行jenkins build [job_name] \n - 重启jenkins  \n  ——————————————  \n   请按着帮助信息输入内容！"""
        return self.menu

    def zabbix_help(self):
        self.menu = """### zabbix菜单
        ---------------
        a. 获取zabbix主机
        b. 获取报警事件
        c. 获取所有用户
        --------------
        请输入你的选择[a-c]
        """
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

        if sign == HTTP_SIGN:
            if content == '1':
                rest = getattr(help, 'zabbix_help')
                return JsonResponse(
                    {"msgtype": "markdown",
                     "markdown": {
                         "title": 'help',
                         "text": rest()
                     },
                     }
                )
            if content in zabbixs.keys():
                print(content)
                rest = getattr(mapping, zabbixs[content])
                print(rest)
                return JsonResponse(
                    {"msgtype": "text",
                     "text": {
                         "content": rest()
                     }
                     }
                )
            if content in jiras.keys():
                rest = getattr(jira, jiras[content])
                print(rest)
                return JsonResponse(
                    {"msgtype": "text",
                     "text": {
                         "content": rest()
                     }
                     }
                )
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
