#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Author: wanger  
#Email: cxf210210@163.com
#File:shell.py
#CreateTime:2020/6/15 16:10
# __Software__: PyCharm
from django.http import HttpResponse, JsonResponse
import json, re,paramiko
from django.core.cache import cache

class shell:
	def __init__(self,content):
		self.user='root'
		self.password='qwe@123..asd'
		self.host_port='22'
		self.content=content

	def ssh(self,exec_comm):
		self.ip = re.search('\[(.*?)\]', self.content).group(1)
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(self.ip, self.host_port, self.user, self.password)
		stdin, stdout, stderr = ssh.exec_command(exec_comm)
		out = stdout.readlines()
		err = stderr.readlines()
		ssh.close()
		return out, err

		return out, err
	def getmem(self):
		exec_comm='free -m'
		result=self.ssh(exec_comm)
		print(result)
		return JsonResponse(
            {"msgtype": "text",
            "text": {
                "content": result
                }
            }
        )

	def getdisk(self):
		exec_comm='df -h'
		result=self.ssh(exec_comm)
		print(result)
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": result
			 }
			 }
		)
	def getport(self):
		port = re.search('\[(.*?)\]\[(.*?)\]', self.content).group(2)
		exec_comm = "netstat -ntlp |egrep -w %s" % port
		result = self.ssh(exec_comm)
		print(result)
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": result
			 }
			 }
		)
	def getlog(self):
		logpath=re.search('\[(.*?)\]\[(.*?)\]', self.content).group(2)
		exec_comm='tail -n 20 %s' %logpath
		result = self.ssh(exec_comm)
		print(result)
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": result
			 }
			 }
		)

	def getservice(self):
		domain=re.search('\[(.*?)\]\[(.*?)\]', self.content).group(2)
		exec_comm='systemctl status %s'%domain
		result = self.ssh(exec_comm)
		print(result)
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": result
			 }
			 }
		)

	def getload(self):
		exec_comm = 'uptime'
		result = self.ssh(exec_comm)
		print(result)
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": result
			 }
			 }
		)
	def restart(self):
		service=re.search('\[(.*?)\]\[(.*?)\]', self.content).group(2)
		exec_comm='systemctl restart %s'%service
		result = self.ssh(exec_comm)
		#return result
		return JsonResponse(
			{"msgtype": "text",
			 "text": {
				 "content": '重启结果'+str(result)
			 }
			 }
		)
def shellres(content):
	shells=shell(content)
	shellreflect={'内存信息':'getmem','磁盘信息':'getdisk','日志信息':'getlog','服务检测':'getservice','端口检测':'getport','负载信息':'getload','重启服务':'restart'}
	for i in shellreflect.keys():

		if '重启服务' in content:

			split=content.split('|')
			print(split)
			if len(split)==2 and split[1]=='是':
				cache.delete('name')
				cache.delete('data')
				#del split
				return shells.restart()
			if len(split)==2 and split[1]=='否':
				cache.delete('name')
				cache.delete('data')
				#del split
				return JsonResponse(
					{"msgtype": "text",
			 		"text": {
				 		"content": '取消重启服务操作'
			 		}
			 		}
			)
			else :
				cache.set('data',content)
				print(cache.get('data'))
				return JsonResponse(
					{"msgtype": "text",
			 		"text": {
				 		"content": '确定要重启服务吗?(是/否)'
			 		}
			 		}
			)

		if i in content:
			rest = getattr(shells, shellreflect[i])
			return rest()
		else:
			continue


	return JsonResponse(
		{"msgtype": "text",
		 "text": {
			 "content": "您输入的格式有错误，请重新输入"
		 }
		 }
	)



