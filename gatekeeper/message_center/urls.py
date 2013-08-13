# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url


urlpatterns = patterns('gatekeeper.message_center.views',
    url(r'^$',"message_list",name="gk_message_list"),
    url(r'^unread/$',"unread_message_inline",name="gk_unread_message"),
    url(r'^read/$',"read_message_inline",name="gk_read_message"),
    url(r'^mark-read/(?P<id>\d+)/$',"mark_read_message",name="gk_mark_message"),
)