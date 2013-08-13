#coding:utf-8

#python imports
import re
from math import floor

# django imports
from django import template
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

#gatekeeper imports
from gatekeeper.message_center.models import NotificationMessage
from gatekeeper.application.models import ApplicationBase
from gatekeeper.application.settings import APP_STATUS_SUBMIT,APP_STATUS_CLOSED,APP_STATUS_REJECTED
from gatekeeper.application.settings import APP_STATUS_IN_GUARD_CHECK,APP_STATUS_OUT_GUARD_CHECK

register = template.Library()

@register.inclusion_tag('core/left_nav.html', takes_context=True)
def left_nav(context):
    """
    生成主頁面中左側導航條
    """
    request = context.get("request")
    
    msg_center_count = NotificationMessage.objects.filter(user=request.user,is_delete=False,is_read=False).count()
    
    not_status = [
        APP_STATUS_SUBMIT,
        APP_STATUS_CLOSED,
        APP_STATUS_REJECTED,
        APP_STATUS_IN_GUARD_CHECK,
        APP_STATUS_OUT_GUARD_CHECK]
    
    app_num = 0
    apps = ApplicationBase.objects.exclude(status__name__in = not_status)
    for app in apps:
        if app.has_signed_perm(user=request.user):
            app_num+=1
    
    tabs =[
        {
            'title':_(u'首頁'),
            'link':reverse('gk_home'),
            'icon':'icon-home',
            },
        {
            'title':_(u'信息中心'),
            'link':reverse('gk_message_list'),
            'icon':'icon-envelope',
            'num':msg_center_count,
            },
        {
            'title':_(u'新申請'),
            'link':reverse('gk_app_new'),
            'icon':'icon-plus',
            },
        {
            'title':_(u'單據簽核'),
            'link':reverse('gk_app_sign_list'),
            'icon':'icon-pencil',
            'num':app_num,
            },
        {
            'title':_(u'我的申請單'),
            'link':reverse('gk_my_app'),
            'icon':'icon-file',
            },
        {
            'title':_(u'單據查找'),
            'link':reverse('gk_app_search'),
            'icon':'icon-search',
            },
        #{
        #    'title':'-',
        #    },

        ]

    for tab in tabs:
        if request.path.find(tab.get('link','')) != -1:
            tab['selected'] = True
            
    return {"tabs": tabs}
