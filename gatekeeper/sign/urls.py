from django.conf.urls import patterns, include, url
from sign.views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('gatekeeper.sign.views',
    #url(r'^$', 'indexpage'),
    url(r'^add$',create_app),
    url(r'^test$',test),
    url(r'^json$',json_device),
    url(r'^savejson$',jsonsave),
    url(r'^testajax$',testajax),
    url(r'^wizard$',wizard),
    url(r'^wizard1$',wizard1),
    url(r'^wizard2$',wizard2),
    url(r'^wizardtest$',wizardtest),

    # Examples:
    # url(r'^$', 'gatekeeper.views.home', name='home'),
    # url(r'^gatekeeper/', include('gatekeeper.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
