from django.conf.urls import patterns, include, url
from views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('gatekeeper.appform.views',
    url(r'^$', indexpage),
    url(r'^create/$',create),
    url(r'^create/step(?P<next_step_idx>\d+)$',create_wizard),#表單嚮導
    url(r'^test/$',create_app),
    url(r'^create/step(?P<step_index>\d+)/(?P<step_current>\d+)/$',wizard),
    url(r'^create/getjson/step(?P<next_step_idx>\d+)/$',wizard_json),
    url(r'^test_select/$',test_select),
    #url(r'^test$',test),
    #url(r'^json$',json_device),
    #url(r'^savejson$',jsonsave),
    #url(r'^testajax$',testajax),
    #url(r'^wizard$',wizard),
    #url(r'^wizard1$',wizard1),
    #url(r'^wizard2$',wizard2),
    #url(r'^wizardtest$',wizardtest),
)
