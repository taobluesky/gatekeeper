from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = patterns('',
    url(r'^home/$','gatekeeper.core.views.home',name='gk_home'),
    url(r'^accounts/',include('account.urls')),
    url(r'^sign/',include('gatekeeper.sign.urls')),
    url(r'^appform/', include('appform.urls')),
    url(r'^auth/', include('auth.urls')),
    
    url(r'^core/',include('core.urls')),
    
    url(r'^application/',include('application.urls')),
    url(r'^message/',include('message_center.urls')),
    url(r'^manage/',include('management.urls')),
    # Examples:
    # url(r'^gatekeeper/', include('gatekeeper.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^tinymce/', include('tinymce.urls')),
)

urlpatterns += patterns("",
    url(r'^download/(?P<path>.*)$',"gatekeeper.core.views.download_view",{'document_root': settings.DOWNLOAD_ROOT, 'show_indexes': False },name="gk_download"),
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)

#urlpatterns += staticfiles_urlpatterns()