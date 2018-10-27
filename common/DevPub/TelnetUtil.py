#-*-coding:utf-8-*-
#!/usr/bin/env python
__author__ = "lixn"
import paramiko
import telnetlib

class LoginDev(object):
    """
    实现ssh,telnet,private_key登录服务器
    """
    def __init__(self,ip,port,username,password,logintype,private_key_path,private_key):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.logintype = logintype
        self.private_key_path = private_key_path
        self.private_key = private_key
        self.ssh = None

    @property
    def connect(self):
        if self.logintype == "ssh" or self.logintype == "SSH":
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ip,self.port,self.username,self.password)
        elif self.logintype == "telnet" or self.logintype == "TELNET":
            self.ssh = telnetlib.Telnet(self.ip)
            self.ssh.read_until("login: ")
            self.ssh.write(self.username + "\n")
            if self.password:
                self.ssh.read_until("Password: ")
                self.ssh.write(self.password + "\n")

        elif self.logintype == "private_key":
            if not self.private_key and self.private_key_path:
                self.private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ip, self.port, self.username, self.private_key)

    def PrintMsg(self,cmd):
        if self.logintype == "telnet" or self.logintype == "TELNET":
            self.ssh.write(cmd)
            return self.ssh.read_all()
        else:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            return stdout.read()

    def LogoutDev(self):
        if self.ssh:
            self.ssh.close()

class SFTP(object):
    """
    实现SFTP功能
    """
    def __init__(self,ip,port,username,password):
        self.t = None
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        self.t = paramiko.Transport((self.ip,self.port))
        self.t.connect(username=self.username,password=self.password)
        self.connection = paramiko.SFTPClient.from_transport(self.t)

    def disconnect(self):
        if self.connection:
            self.t.close()

