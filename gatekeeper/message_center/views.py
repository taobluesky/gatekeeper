# -*- coding: utf-8 -*-

# python imports
#import simplejson

# django imports
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

#gk imports
from .models import NotificationMessage
from gatekeeper.core.utils import LazyEncoder

@login_required
def message_list(request,template_name="message_center/message_list.html"):
    if request.method=="POST":
        action = request.POST.get("action")
        selected_action = request.POST.getlist('selected')
        tab_name = request.POST.get('tab_name')
        if selected_action:
            if action == "read":
                message = NotificationMessage.objects.filter(id__in=selected_action,user=request.user,is_delete=False,is_read=False).update(is_read=True)
            elif action == "delete":
                message = NotificationMessage.objects.filter(id__in=selected_action,user=request.user).update(is_delete=True)

    else:
        tab_name = "unread"
    
    return render_to_response(template_name,RequestContext(request,{
        'tab_name':tab_name,
    }))
    
@login_required
def unread_message_inline(request,template_name="message_center/message_inline.html"):
    if request.is_ajax():
        message_list = NotificationMessage.objects.filter(user=request.user,is_delete=False,is_read=False)
        paginator = Paginator(message_list, 8)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        try:
            messages = paginator.page(page)
        except (EmptyPage, InvalidPage):
            messages = paginator.page(paginator.num_pages)
            
        return render_to_response(template_name,RequestContext(request, {
            "tab_name":"unread",
            "messages_page":messages,
            "page_link_url":reverse("gk_unread_message"),
        }))
    else:
        # 非ajax請求時返回bad request錯誤
        return HttpResponse(status=400)

@login_required
def read_message_inline(request,template_name="message_center/message_inline.html"):
    if request.is_ajax():
        message_list = NotificationMessage.objects.filter(user=request.user,is_delete=False,is_read=True)
        paginator = Paginator(message_list, 8)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        
        try:
            messages = paginator.page(page)
        except (EmptyPage, InvalidPage):
            messages = paginator.page(paginator.num_pages)
            
        return render_to_response(template_name,RequestContext(request, {
            "tab_name":"read",
            "messages_page":messages,
            "page_link_url":reverse("gk_read_message"),
        }))
    else:
        return HttpResponse(status=400)

@login_required
def mark_read_message(request,id):
    """
    當點開列表項時,標記消息為已讀
    """
    try:
        message = NotificationMessage.objects.get(id=id,user=request.user,is_delete=False,is_read=False)
        message.is_read=True
        message.save()
        return HttpResponse("sucess")
    except NotificationMessage.DoesNotExist:
        return HttpResponse("failure")

    