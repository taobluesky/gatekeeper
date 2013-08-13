# -*- coding: utf-8 -*-

#gk imports
from gatekeeper.core.signals import app_created_signal
from gatekeeper.core.signals import app_signed_signal
from gatekeeper.mail import utils as mail_utils

def app_created_listener(sender,**kwargs):
    """
    監聽申請單創建動作
    """
    request = sender.get("request")
    app = sender.get("app")
    mail_utils.send_creted_app_mail(request,app)
    
def app_signed_listener(sender,**kwargs):
    """
    監聽申請單簽核動作
    """
    request = sender.get("request")
    app = sender.get("app")
    mail_utils.send_signed_app_mail(request,app)
    
app_created_signal.connect(app_created_listener)
app_signed_signal.connect(app_signed_listener)