#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  Email:cxf210210@163.com
@Version        :  
------------------------------------
@File           :  xunjian.py
@Description    :  
@CreateTime     :  2020/5/26 23:37
------------------------------------
@ModifyTime     :  
"""
# coding=utf-8
import requests, json, csv, codecs, datetime, time

ApiUrl = 'http://47.103.14.52:8080/api_jsonrpc.php'
header = {"Content-Type": "application/json"}
user = "Admin"
password = "zabbix"
csvheader = ['name', 'ip', 'cipan', 'neicun', 'cpu', 'clock']
x = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
y = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")


def gettoken():
	data = {"jsonrpc": "2.0",
			"method": "user.login",
			"params": {
				"user": user,
				"password": password
			},
			"id": 1,
			"auth": None
			}
	auth = requests.post(url=ApiUrl, headers=header, json=data)
	return json.loads(auth.content)['result']


def timestamp(x, y):
	p = time.strptime(x, "%Y-%m-%d %H:%M:%S")
	starttime = str(int(time.mktime(p)))
	q = time.strptime(y, "%Y-%m-%d %H:%M:%S")
	endtime = str(int(time.mktime(q)))
	return starttime, endtime


def logout(auth):
	data = {
		"jsonrpc": "2.0",
		"method": "user.logout",
		"params": [],
		"id": 1,
		"auth": auth
	}
	auth = requests.post(url=ApiUrl, headers=header, json=data)
	return json.loads(auth.content)


def get_hosts(groupids, auth):
	data = {
		"jsonrpc": "2.0",
		"method": "host.get",
		"params": {
			"output": ["name"],
			"groupids": groupids,
			"filter": {
				"status": "0"
			},
			"selectInterfaces": [
				"ip"
			],
		},
		"auth": auth,
		"id": 1
	}
	gethost = requests.post(url=ApiUrl, headers=header, json=data)
	return json.loads(gethost.content)["result"]


def getitem1(hosts, auth, timestamp):
	# item1=[]
	host = []
	for i in hosts:
		item1 = []
		print(i)
		dic1 = {}
		for j in ['vfs.fs.inode[/,pfree]', 'vm.memory.size[pavailable]', 'system.cpu.load[all,avg15]']:
			data = {
				"jsonrpc": "2.0",
				"method": "item.get",
				"params": {
					"output": [
						"itemid"
						# "key_"
					],
					"search": {
						"key_": j
					},
					"hostids": i['hostid']
				},
				"auth": auth,
				"id": 1
			}
			getitem = requests.post(url=ApiUrl, headers=header, json=data)
			item = json.loads(getitem.content)['result']
			print(item)
			hisdata = {
				"jsonrpc": "2.0",
				"method": "history.get",
				"params": {
					"output": [
						"value",
						"clock"
					],
					"time_from": timestamp[0],
					"time_till":timestamp[1],
					"history": 0,
					"itemids": '%s' % (item[0]['itemid']),
					"limit": 1
				},
				"auth": auth,
				"id": 1
			}
			gethist = requests.post(url=ApiUrl, headers=header, json=hisdata)
			hist = json.loads(gethist.content)['result']
			# gethist(item,timestamp,auth)
			item1.append(hist)
		print(item1)
		dic1['name'] = i['name']
		dic1['ip'] = i['interfaces'][0]['ip']
		dic1['cipan'] = item1[0][0]['value']
		dic1['neicun'] = item1[1][0]['value']
		dic1['cpu'] = item1[2][0]['value']
		x = time.localtime(int(item1[0][0]['clock']))
		item1[2][0]['clock'] = time.strftime("%Y-%m-%d %H:%M:%S", x)
		dic1['clock'] = item1[2][0]['clock']
		host.append(dic1)
	# print(item)
	return host

def writecsv(getitem1):

	with open('/usr/share/nginx/html/data.csv', 'w', encoding='utf-8-sig') as f:
		# f.write(codecs.BOM_UTF8)
		writer = csv.DictWriter(f, csvheader)
		writer.writeheader()

		for row in getitem1:
			writer.writerow(row)

def run():

	token = gettoken()
	timestamps = timestamp(x,y)
	gethost = get_hosts(2, token)

	getitem = getitem1(gethost, token, timestamps)
	# print(getitem1)
	writecsv(getitem)
	logout(token)
if __name__ =='__main__':
    run()

