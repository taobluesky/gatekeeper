# -*- coding: utf-8 -*-
#python imports
from urlparse import urlparse

# django imports
from django.contrib import auth
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson

#gk imports 
import gatekeeper
from gatekeeper.core.utils import LazyEncoder
from gatekeeper.core.utils import set_message_cookie
from gatekeeper.account.models import Employee
from gatekeeper.account.forms import PersonInformationForm

@login_required
def profile(request, template_name="account/profile.html"):
    """保存提交的個人信息.
    """
    employee = request.user.employee
    if request.method == "POST":
        person_infomation_form = PersonInformationForm(user=request.user,
            initial={
            "notes_mail": employee.notes_mail,
            "extension":employee.extension,
            "telephone":employee.telephone,
            }, data=request.POST,
        )
        if person_infomation_form.is_valid():
            employee.notes_mail = person_infomation_form.cleaned_data.get("notes_mail")
            employee.extension = person_infomation_form.cleaned_data.get("extension")
            employee.telephone = person_infomation_form.cleaned_data.get("telephone")
            employee.save()
            
            return set_message_cookie(msg=_(u"修改成功！"),url=reverse("gk_my_profile"))
    else:
        person_infomation_form = PersonInformationForm(user=request.user,
            initial={
            "notes_mail": employee.notes_mail,
            "extension":employee.extension,
            "telephone":employee.telephone,
        })

    return render_to_response(template_name, RequestContext(request, {
        "form": person_infomation_form
    }))
    
@login_required
def password(request, template_name="account/password.html"):
    """修改當前登錄用戶的密碼.
    """
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return set_message_cookie(msg=_(u"修改成功！"),url=reverse("gk_my_password"))
            #return HttpResponseRedirect(reverse("gk_my_password"))
    else:
        form = PasswordChangeForm(request.user)

    return render_to_response(template_name, RequestContext(request, {
        "form": form
    }))
    
@login_required
def account(request, template_name="account/account.html"):
    """顯示當前用戶帳號主頁面.
    """
    user = request.user

    return render_to_response(template_name, RequestContext(request, {
        "user": user,
    }))
    
def login_view(request,template_name="account/login.html"):
    """
    登錄系統
    """
    #login_form = AuthenticationForm()
    #login_form.fields["username"].label = _(u"工號")
    
    if request.method=='POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            # 用戶登錄
            auth.login(request, user)
            # 設置session過期時間
            #request.session.set_expiry(300)
            
            redirect_to = request.POST.get("next")
            # 簡單的安全檢查
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = reverse("gk_home")
                
            return HttpResponseRedirect(redirect_to)
            
        else:
            error = True

    else:
        username = ''
        error = False
    
    # Get next_url
    next_url = request.REQUEST.get("next")
    if next_url is None:
        next_url = request.META.get("HTTP_REFERER")
    if next_url is None:
        next_url = reverse("gk_home")

    # Get just the path of the url. See django.contrib.auth.views.login for more
    next_url = urlparse(next_url)
    next_url = next_url[2]
    
    return render_to_response(template_name,RequestContext(request,{
        'error':error,
        'username':username,
        "next_url": next_url,
    }))

def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("gk_login"))
