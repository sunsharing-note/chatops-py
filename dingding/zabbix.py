#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Author: wanger  
#Email: cxf210210@163.com
#File:zabbix.py
#CreateTime:2020/6/15 16:21
# __Software__: PyCharm

import re,requests,json
from chatops.settings import *
from django.http import HttpResponse, JsonResponse
import time
from . import xunjian

zabbix_url = ZABBIX_URL
zabbix_user = ZABBIX_USER
zabbix_password = ZABBIX_PASSWORD
headers = {"Content-Type": "application/json"}
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
        temp = func(*args)
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

class zabbix:

	def __init__(self,content):
		self.content=content
    #@staticmethod
	@zabbix_loginout
	def gethost(self):
		self.ip = re.search('\[(.*?)\]',self.content).group(1)
        # print("gethost auth:", auth)
		data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend",
				"filter": {
					"host": [
						"%s" %self.ip
					]
				}
            },
            "auth": auth,
            "id": 1
        }
        # print("gethost data:", data)
		gethost = requests.post(url=zabbix_url, headers=headers, json=data)
		gethost = json.loads(gethost.content)['result']
        # print("gethost:", gethost)
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": gethost
			 }
			 }
		)

	@zabbix_loginout
	def getalert(self):
		self.ip = re.search('\[(.*?)\]', self.content).group(1)
		data = {
            "jsonrpc": "2.0",
            "method": "event.get",
            "params": {
                "output": "extend",
                "select_acknowledges": "extend",
                "selectTags": "extend",
                "sortfield": ["clock", "eventid"],
                "sortorder": "DESC",
				"filter": {
					"host": [
						"%s" % self.ip
					]
				}

            },
            "auth": auth,
            "id": 1
        }
		getalert = requests.post(url=zabbix_url, headers=headers, json=data)
		getalert = json.loads(getalert.content)['result']
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": getalert
			 }
			 }
		)

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
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": getuser
			 }
			 }
		)
	def getversion(self):
		data={
    		"jsonrpc": "2.0",
    		"method": "apiinfo.version",
    		"params": [],
    		"id": 1
		}
		getversion = requests.post(url=zabbix_url, headers=headers, json=data)
		getversion = json.loads(getversion.content)['result']
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": getversion
			 }
			 }
		)

	@zabbix_loginout
	def getevent(self):
		starttime=str(int(time.time()-3600))
		endtime=str(int(time.time()))
		data={
    		"jsonrpc": "2.0",
    		"method": "event.get",
    		"params": {
        		"output": "extend",
        		"time_from": starttime,
        		"time_till": endtime,
        		"sortfield": ["clock", "eventid"],
        		"sortorder": "desc"
    		},
    		"auth": auth,
    		"id": 1
		}
		getevent = requests.post(url=zabbix_url, headers=headers, json=data)
		getevent = json.loads(getevent.content)['result']
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": getevent
			 }
			 }
		)


def zabbixres(content):
	zabbixs = zabbix(content)
	if '所有用户' in content:
		return zabbixs.getzabbixuser()
	if '版本信息' in content:
 		return zabbixs.getversion()
	if '报警信息' in content:
 		return zabbixs.getalert()
	if '主机信息' in content:
		return zabbixs.gethost()
	if '事件信息' in content:
		return zabbixs.getevent()
	if '巡检表' in content:
		xunjian.run()
		return JsonResponse(
			{
				"msgtype": "markdown",
				"markdown": {
					"title": "ZABBIX巡检",
					"text": " [巡检表](https://www.xyzabbix.cn/data.csv) \n"
				}
			}
		)
	else:
		return JsonResponse(
			{"msgtype": "text",
	 		"text": {
		 		"content": "您输入的格式有错误，请重新输入"
	 		}
			}
		)


