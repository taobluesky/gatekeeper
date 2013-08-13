# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

urlpatterns = patterns('gatekeeper.core.views',
    url(r'^API/get-emp-info/$',"get_emp_info",name="gk_get_emp_info"),
)