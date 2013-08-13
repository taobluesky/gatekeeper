# -*- coding: utf-8 -*-

# python imports
import logging
import threading
from suds.client import Client
#gk imports
from gatekeeper import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_mail(subject,body,to):
    MessageCenterEmail(subject=subject,body=body,to=to).send()
    
class MessageCenterEmail(object):
    """
    使用Message Center发送邮件
    """
    client = None
    
    def __init__(self,subject,body,to,cc=''):
        self.subject = subject
        self.body = body
        self.to = to
        self.cc = cc
        self.from_email = settings.MESSAGE_CENTER_FROM_EMAIL
        #self._lock = threading.RLock()
        
    def open(self):
        if MessageCenterEmail.client:
            # 已经存在client，就直接返回。。
            return False
        try:
            MessageCenterEmail.client = Client(settings.MESSAGE_CENTER_URL)
            header = MessageCenterEmail.client.factory.create('AuthenticationSoapHeader')
            header.UserId = settings.MESSAGE_CENTER_USER
            header.Password = settings.MESSAGE_CENTER_PASSWORD
            MessageCenterEmail.client.set_options(soapheaders=header)
            return True
        except:
            raise 
            
    def send(self):
        self.open()
        # 创建新线程来发送邮件
        threading.Thread(target=self._send,args=()).start()
        
    def _send(self):
        try:
            if MessageCenterEmail.client is None:
                # 出现未知错误 直接返回。。
                logger.warning('message center client is error')
                return
            send_group_mail_status = MessageCenterEmail.client.service.SendGroupMails(
                To=self.to,
                Cc=self.cc,
                Subject=self.subject,
                Body=self.body,
                SmtpId=self.from_email,
                SmtpPassowrd='',
                SmtpAddress=self.from_email,
                NoteAddress='',
                NotesPassword='',
            )
            logger.info('the mail is sent!')
        except:
            pass
        # Message center返回的格式:["收件地址,是否調用成功1(成功)/0(失敗),消息唯一編號,錯誤原因"]
        # print type(send_group_mail) <type 'instance'>
        '''
        status_list = send_group_mail_status.string
        status_str = status_list[0]
        status = status_str.split(',')
        if status[1]=='1':
            is_send = True
        elif status[1]=='0':
            is_send = False
        '''

def __send_super_mail_by_soap(subject,body,to='',from_mail='ces-it-tech@mail.foxconn.com',cc=''):
    """
    使用Message center發送supper notes郵件
    """
    try:
        url = 'http://msgcenter.ecmms.foxconn:2571/Messaging.asmx?WSDL'

        client = Client(url)
        header = client.factory.create('AuthenticationSoapHeader')
        header.UserId = 'GateKeeperUid'
        header.Password = 'GateKeeperPwd'
        client.set_options(soapheaders=header)

        send_group_mail_status = client.service.SendGroupMails(
            To=to,
            Cc=cc,
            Subject=subject,
            Body=body,
            SmtpId=from_mail,
            SmtpPassowrd='',
            SmtpAddress=from_mail,
            NoteAddress='',
            NotesPassword='',
        )
        # Message center返回的格式:["收件地址,是否調用成功1(成功)/0(失敗),消息唯一編號,錯誤原因"]
        # print type(send_group_mail) <type 'instance'>
        status_list = send_group_mail_status.string
        status_str = status_list[0]
        status = status_str.split(',')
        if status[1]=='1':
            is_send = True
        elif status[1]=='0':
            is_send = False
    except:
        is_send = False
        
    return is_send
      