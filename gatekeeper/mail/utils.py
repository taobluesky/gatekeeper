# -*- coding: utf-8 -*-

# django imports
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template.base import TemplateDoesNotExist

# gk imports
from gatekeeper.mail import mail
from gatekeeper.application.models import ApplicationHistory
from gatekeeper.application.models import ApplicationBase

from gatekeeper.application.settings import APP_STATUS_IN_GUARD_CHECK
from gatekeeper.application.settings import APP_STATUS_OUT_GUARD_CHECK
from gatekeeper.application.settings import APP_STATUS_REJECTED
from gatekeeper.application.settings import APP_STATUS_IT_INSPECT
from gatekeeper.application.settings import ROUTE_ACTION_SUBMIT
from gatekeeper.application.settings import ROUTE_ACTION_AGREE
from gatekeeper.application.settings import ROUTE_ACTION_REJECT
from gatekeeper.application.settings import ROUTE_ACTION_DONE

  
def send_creted_app_mail(request,app):
    """
    發送郵件 通知用戶 申請單成功創建
    """
    #try:
    #    subject = render_to_string("mail/created_app_subject.txt")
    #except TemplateDoesNotExist:
    subject = _(u" 您在《ＧＡＴＥＫＥＥＰＥＲ》系統中申請已成功提交")
    unsigner_list = app.get_unsigner_list()
    history = ApplicationHistory.objects.filter(application=app)
    body_content = render_to_string("mail/created_content.html",{
            "app":app,
            "site":"http://%s" % Site.objects.get(id=settings.SITE_ID),
        })
        
    html = render_to_string("mail/signed_app_mail.html",{
        "is_user":True,
        "signer":signer,
        "app":app,
        "body_content":body_content,
        "history":history,
        "unsigner_list":unsigner_list,
        "ROUTE_ACTION_REJECT":ROUTE_ACTION_REJECT,
    })
    
    to = app.get_submit_email()

    mail.send_mail(subject=subject,body=html,to=to)
    
def send_notify_inspect(app):
    """
    發郵件通知用戶攜帶設備至IT進行資安檢查
    """
    signer = app.submit.employee
    to = signer.notes_mail
    subject = _(u"您在《ＧＡＴＥＫＥＥＰＥＲ》的申請單已經進入資安檢查階段")
    body_content = render_to_string("mail/notify_inspect_content.html",{
        "app":app,
        "site":"http://%s" % Site.objects.get(id=settings.SITE_ID),
    })
    
    unsigner_list = app.get_unsigner_list()
    history = ApplicationHistory.objects.filter(application=app)
    
    html = render_to_string("mail/signed_app_mail.html",{
        "is_user":True,
        "signer":signer,
        "app":app,
        "body_content":body_content,
        "history":history,
        "unsigner_list":unsigner_list,
        "ROUTE_ACTION_REJECT":ROUTE_ACTION_REJECT,
    })
    mail.send_mail(subject=subject,body=html,to=to)
    
def send_signed_app_mail(request,app): 
    """
    發送邮件 通知主管和用户 申請單簽核狀態
    """
    if not isinstance(app,ApplicationBase):
        return
    unsigner_list = app.get_unsigner_list()
    history = ApplicationHistory.objects.filter(application=app)
        
    if app.status.name in [APP_STATUS_IN_GUARD_CHECK,APP_STATUS_OUT_GUARD_CHECK]:
        # 簽核完成 通知用戶
        is_user = True
        subject = _(u"您在《ＧＡＴＥＫＥＥＰＥＲ》的申請已經簽核完成！")
        signer = app.submit.employee
        body_content = render_to_string("mail/done_content.html",{
            "app":app,
            "site":"http://%s" % Site.objects.get(id=settings.SITE_ID),
        })

    elif app.status.name == APP_STATUS_REJECTED:
        is_user = True
        try:
            subject = render_to_string("mail/rejected_subject.txt",{"app":app})
        except TemplateDoesNotExist:
            subject = _(u"您在《ＧＡＴＥＫＥＥＰＥＲ》的申請單被拒，請查看！")
        signer = app.submit.employee
        body_content = render_to_string("mail/rejected_content.html",{
            "app":app,
            "reject_history":history.latest('id'),
            "site":"http://%s" % Site.objects.get(id=settings.SITE_ID),
        })
    elif app.status.name == APP_STATUS_IT_INSPECT:
        send_notify_inspect(app)
        is_user = False
        subject = _(u"《ＧＡＴＥＫＥＥＰＥＲ》申請單已經進入資安檢查階段")
        signer = unsigner_list[0]['signer']
        body_content = render_to_string("mail/inspect_content.html",{
            "app":app,
            "site":"http://%s" % Site.objects.get(id=settings.SITE_ID),
        })
    else:
        is_user = False
        try:
            subject = render_to_string("mail/signed_subject.txt",{"app":app})
        except TemplateDoesNotExist:
            subject = _(u"請您簽核《ＧＡＴＥＫＥＥＰＥＲ》申請單")
        signer = unsigner_list[0]['signer']
        body_content = render_to_string("mail/signed_content.html",{
            "app":app,
            "site":"http://%s" % Site.objects.get(id=settings.SITE_ID),
        })
    
    if signer:
        to = signer.notes_mail
    else:
        return
    
    html = render_to_string("mail/signed_app_mail.html",{
        "is_user":is_user,
        "signer":signer,
        "app":app,
        "body_content":body_content,
        "history":history,
        "unsigner_list":unsigner_list,
        "ROUTE_ACTION_REJECT":ROUTE_ACTION_REJECT,
    })
    mail.send_mail(subject=subject,body=html,to=to)
    
    
def test():
    from gatekeeper.application.models import ApplicationBase
    app = ApplicationBase.objects.filter(number='TJCARRY1307170001071D')[0]
    send_signed_app_mail(None,app)
    
    
    
    