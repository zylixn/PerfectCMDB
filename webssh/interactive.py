import socket
import sys
from paramiko.py3compat import u
from django.utils.encoding import smart_bytes

try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False
    # raise Exception('This project does\'t support windows system!')
try:
    import simplejson as json
except ImportError:
    import json

import threading
import time

def interactive_shell(chan, channel):
    if has_termios:
        posix_shell(chan, channel)
    else:
        windows_shell(chan,channel)

# from webssh.asgi import channel_layer #正式运行时daphne 不支持

def windows_shell(chan,channel):
    import threading

    sys.stdout.write(
        "Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n"
    )

    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write("\r\n*** EOF ***\r\n\r\n")
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass

def posix_shell(chan, channel):
    # print 3,'webssh.interactive'
    from webssh.asgi import channel_layer
    # channel_layer = channel_layer2()
    try:
        chan.settimeout(0.0)
        while 1:
            # 循环监视ssh终端输出，实时发给websocket客户端显示
            if not chan.recv_ready():
                time.sleep(0.1)
                continue
            try:
                x = chan.recv(1024)  # 收取ssh-tty打印信息，带着色
                while ord(x[-1]) > 127:
                    # utf8字符为3位，有时截取时结尾刚好碰到utf8字符，导致汉字被分割成二部分
                    try:
                        x += chan.recv(1)
                    except:
                        break
                print(x, 888)
                if len(x) == 0:
                    channel_layer.send(channel, {'text': json.dumps(['disconnect', smart_bytes('\r\n*** EOF\r\n')])})
                    break
                channel_layer.send(channel, {'text': json.dumps(['stdout', smart_bytes(x)])})  # 发送信息到web SSH显示
            except socket.timeout:
                pass
            except UnicodeDecodeError as e:
                print(e)
                lines = x.splitlines()
                for line in lines:
                    # recv(1024字节)，除乱码字符所在行外，将其它行正常显示
                    if line:
                        try:
                            channel_layer.send(channel, {'text': json.dumps(['stdout', '%s\r\n' % smart_bytes(line)])})
                        except UnicodeDecodeError as e:
                            channel_layer.send(channel, {'text': json.dumps(['stdout', 'Error: utf-8编码失败！！！\r\n%s\r\n' % smart_bytes(e)], )})

            except Exception as e:
                channel_layer.send(channel, {'text': json.dumps(['stdout', 'Error: 连接意外中断.' + smart_bytes(e)], )})
                break

    finally:
        print('连接断开..', channel)
        pass
