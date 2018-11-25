import requests
import paramiko
from requests.exceptions import ConnectionError
import json
import ssl
import os
import zipfile

class GitHub(object):
    """建立基于github的相关信息"""
    def __init__(self,username):
        self.username = username
        self.repos = dict()

    def getrepos(self,method="get"):
        """获取账号所有的项目信息"""
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://api.github.com/users/{username}/repos".format(username=self.username)
        try:
            if method == "get":
                response = requests.get(url,verify=False)
            elif method == "post":
                response = requests.post(url,verify=False)
        except ConnectionError as e:
            return None
        self.repos = json.loads(response.content)
        return self.repos

    def getbranches(self,name):
        """获取分枝信息"""
        url = "https://api.github.com/repos/{username}/{name}/branches".format(username=self.username,name=name)
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://api.github.com/users/{username}/repos".format(username=self.username)
        try:
            response = requests.get(url, verify=False)
        except ConnectionError as e:
            return ''
        content = json.loads(response.content)
        return content

    def gettags(self,name):
        """获取所有tag对应的版本"""
        url = "https://api.github.com/repos/{username}/{name}/git/tags".format(username=self.username,name=name)
        ssl._create_default_https_context = ssl._create_unverified_context
        url = "https://api.github.com/users/{username}/repos".format(username=self.username)
        try:
            response = requests.get(url, verify=False)
        except ConnectionError as e:
            return ''
        content = json.loads(response.content)
        return content

class Jenkins(object):
    """自动构建/测试软件"""
    pass

class AutoDeploy(object):
    """实现自动化部署"""
    def __init__(self,local_dir,url):
        self.local_dir = local_dir
        self.url = url
        # 改变脚本的工作目录
        os.chdir(local_dir)

    def download(self,method="get"):
        """基于git的下载对应版本的程序"""
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            if method == "get":
                response = requests.get(self.url,verify=False)
            elif method == "post":
                response = requests.post(self.url,verify=False)
        except ConnectionError as e:
            return None
        content = json.loads(response.content)
        return content

    def unpack(self,filetype="zip"):
        """安装对应版本的程序"""
        pass

    def pack(self,filename,filetype="zip"):
        pass

class SFTP(object):
    """实现sftp功能"""
    def __init__(self,logintype,host,port,username,password,pri_file):
        self.logintype = logintype
        self.username = username
        self.pri_file= pri_file
        self.password = password
        self.host = host
        self.port = port
        self.sftp = ""
        self.transport = ""

    def createsess(self):
        """建立sftp连接"""
        if self.logintype == "password":
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username,password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        else:
            if os.path.isfile(self.pri_file):
                private_key = paramiko.RSAKey.from_private_key_file(self.pri_file)
                self.transport = paramiko.Transport((self.host, self.port))
                self.transport.connect(username=self.username, pkey=private_key)
                self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def put(self,local_file,remote_file):
        if self.sftp:
            self.sftp.put(local_file,remote_file)

    def __del__(self):
        if self.transport:
            self.transport.close()
