
import socks
import socket
import urllib

socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "10.66.21.57", 6131)
socket.socket = socks.socksocket

#print urllib.urlopen("http://www.baidu.com/").read()

from django.core.mail import send_mail
send_mail('Subject here', 'Here is the message.', '605745@qq.com',['605745@qq.com'], fail_silently=False)