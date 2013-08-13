# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('gatekeeper.application.views',
    url(r'^new/$',"app_new",name="gk_app_new"),
    url(r'^new/carry/$',"app_new_carry",name="gk_app_new_carry"),
    url(r'^new/card/$',"app_new_card",name="gk_app_new_card"),
    
    url(r'^create/$',"app_create",name="gk_app_create"),
    url(r'^create-step(?P<index>\d+)/$',"app_step",name="gk_app_step"),
    
    #url(r'^create/step(?P<step_index>\d+)/$',"app_wizard"),
    #url(r'^create/getjson/step(?P<step_index>\d+)/$',"app_wizard_json"),
    url(r'^sign-list/$',"app_list",name="gk_app_sign_list"),
    url(r'^sign-list/detail/(?P<app_id>[^/]+)/$',"app_detail",name="gk_app_detail"),
    url(r'^my/$',"my_app",name="gk_my_app"),
    
    url(r'^download/(?P<app_id>[^/]+)$',"app_download",name="gk_app_download"),

        
    url(r'^signed/(?P<app_id>[^/]+)/$',"app_signed_view",name="gk_app_signed"),
    url(r'^search/$',"app_search",name="gk_app_search"),
    
    url(r'^test/$',"view_test",name="gk_test"),
    #url(r'^test_form/$',"view_form"),
    #url(r'^test$',test),
    #url(r'^json$',json_device),
    #url(r'^savejson$',jsonsave),
    #url(r'^testajax$',testajax),
    #url(r'^wizard$',wizard),
    #url(r'^wizard1$',wizard1),
    #url(r'^wizard2$',wizard2),
    #url(r'^wizardtest$',wizardtest),
)
