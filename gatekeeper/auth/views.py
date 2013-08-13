# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from gatekeeper.auth.models import *
from gatekeeper.auth import login as auth_login,logout as auth_logout,authenticate
from django.utils.translation import ugettext_lazy as _

def my_view(request):
    text = _("Welcome")
    print request.META['REMOTE_ADDR']
    return render_to_response('i18n.html',
                              {"welcome_text":text,
                              "price":888,
                              "org_price":999},
                              context_instance=RequestContext(request))
    #return HttpResponse(text)
    
def login_view(request,loginpage,error_message=None):
    
    if request.method=='POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            if username and password:
                user_cache = authenticate(username=username, password=password)
                if user_cache:
                    # Okay,完成安全檢查.接著讓用戶登錄.
                    auth_login(request,user_cache)
                    # 設置session過期時間為300秒
                    request.session.set_expiry(300)
                    return HttpResponseRedirect('/info/center/')
                else:
                    error_message = u'用戶名或者密碼錯誤！'
            else:
                error_message = u'用戶名或者密碼不能為空！'
        else:
            error_message = u'閒置時間太長或者您的流覽器未打開COOKIES功能！'
    else:
        username = '';
    request.session.set_test_cookie()
    # print request.user.username
    #t = get_template('auth/login_form.html')
    #c = RequestContext(request,locals())
    context = {
        'loginpage':loginpage,
        'username':username,
        'error_message':error_message,
    }
    #return HttpResponse(t.render(c))
    return render_to_response('auth/login_form.html',context,
                              context_instance=RequestContext(request))

def logout_view(request):
    """
    登出用戶,并顯示登出提示信息.
    """
    auth_logout(request)
    return login_view(request,loginpage=True,error_message='您已經成功登出！')
    #return HttpResponseRedirect(reverse(login_view))
