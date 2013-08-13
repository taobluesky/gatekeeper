# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

urlpatterns = patterns('gatekeeper.account.views',
    url(r'^login/$',  "login_view",name="gk_login"),
    url(r'^logout/$', "logout_view",name="gk_logout"),
    
    url(r'^my-profile', "profile", name="gk_my_profile"),
    url(r'^my-password', "password", name="gk_my_password"),
    url(r'^$', "account", name="gk_my_account"),
    
)
