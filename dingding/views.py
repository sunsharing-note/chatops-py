#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# __author__ = 'bigc'
# @Time    : 2020/4/12 21:44
# @Email   : luocs1@lenovo.com
# views部分代码

from django.http import HttpResponse, JsonResponse
import json,re
from chatops.settings import *
import hmac
import hashlib
import base64,requests
from jira import JIRA


# 机器人的app_secret
app_secret = "fkyymqRK_Jr-nmKX4tk9ogMn9OmT87HeDmeJC6Gt30JeRwLQcR94PEf_UwX0EiKi"
#app_secret="D_3RLRTqq76GGePa7XlVWVuaO3fnIlRbkpSCAhrnpTnrIK81Vp1vvBP5-65zWN0E"
zabbix_url=ZABBIX_URL
zabbix_user=ZABBIX_USER
zabbix_password=ZABBIX_PASSWORD
headers = {"Content-Type": "application/json"}
# Create your views here.
class mapping:
    def __init__(self):
        self.auth1=self.auth()
    def auth(self):
        data = {"jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": zabbix_user,
                    "password": zabbix_password
                },
                "id": 1,
                "auth": None
                }
        auth = requests.post(url=zabbix_url, headers=headers, json=data)
        auth = json.loads(auth.content)['result']
        return auth


    def logout(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.logout",
            "params": [],
            "id": 1,
            "auth": self.auth1
        }
        print(self.auth)
        logout = requests.post(url=zabbix_url, headers=headers, json=data)
        logout = json.loads(logout.content)
        return logout

    def gethost(self):

        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend"
            },
            "auth": self.auth1,
            "id": 1
        }

        gethost = requests.post(url=zabbix_url, headers=headers, json=data)
        gethost = json.loads(gethost.content)['result']
        return gethost


    def getalert(self):
        print(self.auth1)
        data={
            "jsonrpc": "2.0",
            "method": "event.get",
            "params": {
                "output": "extend",
                "select_acknowledges": "extend",
                "selectTags": "extend",
                "sortfield": ["clock", "eventid"],
                "sortorder": "DESC"
            },
            "auth": self.auth1,
            "id": 1
        }
        getalert=requests.post(url=zabbix_url,headers=headers,json=data)
        getalert=json.loads(getalert.content)['result']
        return getalert
    def getzabbixuser(self):
        data={
            "jsonrpc": "2.0",
            "method": "user.get",
            "params": {
                "output": [
                    "alias",
                    "name"
                ]
            },
            "auth": self.auth1,
            "id": 1
        }
        getuser=requests.post(url=zabbix_url,headers=headers,json=data)
        getuser=json.loads(getuser.content)['result']
        return getuser
class jira:
    def __init__(self):
        self.options={"server": "http://60.205.177.168:500"}
    def getjiraitem(self):
        # options = {"server": "http://60.205.177.168:500"}
        jira = JIRA(basic_auth=("admin", "asd123456"), options=self.options)
        projects = jira.projects()
        return str(projects)

zabbixs={'登录zabbix':'auth','注销zabbix':'logout','获取zabbix主机':'gethost','获取告警事件':'getalert','获取zabbix用户':'getzabbixuser'}
jiras={'获取jira项目':'getjiraitem'}
mapping=mapping()
jira=jira()
def robot(request):
    if request.method == "POST":
        HTTP_SIGN = request.META.get("HTTP_SIGN")
        HTTP_TIMESTAMP = request.META.get("HTTP_TIMESTAMP")
        res = json.loads(request.body)
        #print(res)
        #print(zabbix_url)
        # 用户输入钉钉的信息
        content = res.get("text").get("content").strip()
        #print(content)
        string_to_sign = '{}\n{}'.format(HTTP_TIMESTAMP, app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(app_secret.encode("utf-8"), string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        #print(sign)
        #print(HTTP_SIGN)
        # 验证签名是否为钉钉服务器发来的

        if sign == HTTP_SIGN:
            if content in zabbixs.keys():
                print(content)
                rest=getattr(mapping,zabbixs[content])
                print(rest)
                return JsonResponse(
                    {"msgtype": "text",
                     "text": {
                         "content": rest()
                     }
                     }
                )
            if content in jiras.keys():
                rest=getattr(jira,jiras[content])
                print(rest)
                return JsonResponse(
                    {"msgtype": "text",
                     "text": {
                         "content": rest()
                     }
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
