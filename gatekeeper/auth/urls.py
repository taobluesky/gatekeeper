from django.conf.urls import patterns, include, url
from views import *

urlpatterns = patterns('gatekeeper.auth.views',
    url(r'^login/$',login_view,{'loginpage':True}),
    url(r'^logout/$',logout_view),
    url(r'^i18n/$',my_view),
)
