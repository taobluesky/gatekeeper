# -*- coding: utf-8 -*-

# python imports
#import json
from datetime import date,datetime

# django imports
from django.conf import settings
from django import forms
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.template.loader import get_template
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.db import connection,transaction
from django.db.models.query import QuerySet
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# gk imports
from gatekeeper.account.models import Employee
from .models import *
from .utils import create_card_emp
from .utils import create_card_customer
from .utils import create_card_customer_onsite
from .utils import create_carry_inout
from .utils import save_application_carry_util
from gatekeeper.core.utils import LazyEncoder
from gatekeeper.core.signals import app_created_signal,app_signed_signal
from .forms import CustomerCardForm,CarryForm,AppTypeForm,DeviceForm,EmployeeForm,CustomerForm,CommentForm,AttachmentForm
from .settings import APP_TYPE_CARRY_INOUT
from .settings import APP_TYPE_CARRY_IN
from .settings import APP_TYPE_CARRY_OUT
from .settings import APP_TYPE_CARD_EMP
from .settings import APP_TYPE_CARD_CUSTOMER
from .settings import APP_TYPE_CARD_CUSTOMER_ONSITE
from .settings import APP_STATUS_MAKE_CARD
from .settings import APP_STATUS_SUBMIT,APP_STATUS_CLOSED,APP_STATUS_REJECTED
from .settings import APP_STATUS_IN_GUARD_CHECK,APP_STATUS_OUT_GUARD_CHECK
from .settings import ROUTE_ACTION_SUBMIT,ROUTE_ACTION_AGREE,ROUTE_ACTION_REJECT,ROUTE_ACTION_DONE
from .forms import ApplicationCarryForm,ApplicationCardForm,DeviceForm_
from core.views import download_view

def convert_to_builtin_type(obj): 
    print type(datetime)
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S') 
    elif isinstance(obj, date): 
        return obj.strftime('%Y-%m-%d') 
    else: 
        raise TypeError('%r is not JSON serializable' % obj)

class JsonResponse(HttpResponse):
    """
    返回JsonResponse
    """
    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serializers.serialize('json', object)
        else:
            content = json.dumps(object,default=convert_to_builtin_type)
        super(JsonResponse, self).__init__(content, mimetype='application/json')

def dictfetchall(cursor):
    """
    将游标返回的结果保存到一个字典对象中
    """
    desc = cursor.description
    return [
    dict(zip([col[0] for col in desc], row))
    for row in cursor.fetchall()
    ]

    
def save_post_to_session(request,stepnumber):
    """
    存儲post data到session
    """
    keylist = request.POST.keys()
    step_session ={}
    for key in keylist:
        step_session[key] = request.POST[key]
    request.session[stepnumber] = step_session
    
def employee_info_inline(request,prefix="",template_name="application/employee_info_inline.html"):
    form = EmployeeForm(initial={"grade":3},prefix=prefix)
    return render_to_string(template_name,RequestContext(request, {
        "form":form,
    }))
    
def customer_info_inline(request,template_name="application/customer_info_inline.html"):
    form = CustomerForm(request.POST)
    return render_to_string(template_name,RequestContext(request, {
        "form":form,
    }))
    
def device_info_inline(request,show_owner=True,template_name="application/device_info_inline.html"):
    form = DeviceForm(request.POST)
    return render_to_string(template_name,RequestContext(request, {
        "show_owner":show_owner,
        "form":form,
    }))

def attachment_upload_inline(request,template_name="application/attachment_upload_inline.html"):
    form = AttachmentForm(request.POST,request.FILES)
    return render_to_string(template_name,RequestContext(request, {
        "form":form,
    }))
    
def comment_inline(request,template_name="application/comment_inline.html"):
    form = CommentForm(request.POST)
    return render_to_string(template_name,RequestContext(request, {
        "form":form,
    }))

@login_required
def app_new(request,template_name="application/app_new.html"):
    #app_type_form = AppTypeForm()
    
    return render_to_response(template_name,RequestContext(request,{
    }))

@login_required
def app_new_carry(request,template_name="application/app_new_carry.html"):
    if request.method == "POST":
        device_form = DeviceForm_(request.POST)
        
        carry_form = ApplicationCarryForm(
            user = request.user,
            data = request.POST,
            files = request.FILES
        )
        
        if device_form.is_valid() and carry_form.is_valid():
            save_application_carry_util(request,device_form,carry_form)
    else:
        emp = Employee.objects.get(emp_no = request.user.employee.emp_no)
        init_data = {
            "emp_no":emp.emp_no,
            "emp_name":emp.name,
            "notes_mail":emp.notes_mail,
            "emp_extension":emp.extension,
            "emp_telephone":emp.telephone,
            "emp_grade":emp.grade,
            "emp_position":emp.position,
            "emp_department":emp.department.name,
        }
            
        device_form = DeviceForm_()
        carry_form = ApplicationCarryForm(user=request.user)
    
    return render_to_response(template_name,RequestContext(request,{
        "device_form":device_form,
        "carry_form":carry_form,
    }))

    
@login_required
def app_new_card(request):
    pass
    
@login_required
def app_create(request):
    app_type_form = AppTypeForm()
    return render_to_response('application/create.html',RequestContext(request,{
        "app_type_form":app_type_form,
    }))

@login_required
def app_step(request,index):
    """
    創建申請單嚮導 視圖函數
    """
    if request.is_ajax():
        form = AppTypeForm(request.POST)
        if form.is_valid() :
            app_type = form.cleaned_data['app_type']
            
        # STEP 1
        if index == '1':
            if app_type in [APP_TYPE_CARD_EMP,APP_TYPE_CARD_CUSTOMER_ONSITE,APP_TYPE_CARD_CUSTOMER]:
                html = step_card_inline(request,app_type)
            elif app_type == APP_TYPE_CARRY_INOUT:
                html = step_carry_inline(request)
        
        # STEP 2
        if index == '2':
            print request.POST
            device_form = DeviceForm(request.POST)
            attachment_form = AttachmentForm(request.POST,request.FILES)
            
            data ={}
            if app_type == APP_TYPE_CARRY_INOUT:
                carry_form = CarryForm(request.POST)
                customer_form = CustomerForm(request.POST)
                receiver_form = EmployeeForm(request.POST,prefix="receiver")
                employee_form = EmployeeForm(request.POST)
                # 測試3個FORM驗證成功
                if carry_form.is_valid() and device_form.is_valid() and attachment_form.is_valid():
                    app_basic = create_carry_inout(request,
                        carry_form,
                        customer_form,
                        receiver_form,
                        employee_form,
                        device_form,
                        attachment_form
                    )
                    data["app_no"] = app_basic.number
                
            elif app_type == APP_TYPE_CARD_EMP:
                employee_form = EmployeeForm(request.POST)
                comment_form = CommentForm(request.POST)
                if device_form.is_valid() and employee_form.is_valid() and comment_form.is_valid() and attachment_form.is_valid():
                    app_basic = create_card_emp(request,device_form,employee_form,comment_form,attachment_form)
                    data["app_no"] = app_basic.number
                    
            elif app_type == APP_TYPE_CARD_CUSTOMER_ONSITE:
                customer_form = CustomerForm(request.POST)
                comment_form = CommentForm(request.POST)
                if device_form.is_valid() and customer_form.is_valid() and comment_form.is_valid() and attachment_form.is_valid():
                    app_basic = create_card_customer_onsite(request,device_form,customer_form,comment_form,attachment_form)
                    data["app_no"] = app_basic.number
                    
            elif app_type == APP_TYPE_CARD_CUSTOMER:
                customer_form = CustomerForm(request.POST)
                customer_card_form = CustomerCardForm(request.POST)
                comment_form = CommentForm(request.POST)
                if device_form.is_valid() and customer_form.is_valid() and comment_form.is_valid() \
                    and attachment_form.is_valid() and customer_card_form.is_valid():
                    app_basic = create_card_customer(request,device_form,customer_form,customer_card_form,comment_form,attachment_form)
                    data["app_no"] = app_basic.number
            
            if data:
                html = step_done(request,data)
                app_basic.handle_submit_status()
                
                app_signed_signal.send({'request':request,'app':app_basic})
                #app_created_signal.send({'request':request,'app':app_basic})
            
    result = simplejson.dumps({
        "html": html,
        "status": "success",
    }, cls=LazyEncoder)
    return HttpResponse(result)
    
def step_carry_inline(request,template_name="application/step_carry.html"):
    form = CarryForm()
    return render_to_string(template_name,RequestContext(request, {
        "form":form,
        "applicant_customer_inline":customer_info_inline(request),
        "applicant_receiver_inline":employee_info_inline(request,prefix="receiver"),
        "applicant_employee_inline":employee_info_inline(request),
        "device_info_inline":device_info_inline(request),
        "attachment_upload_inline":attachment_upload_inline(request),
    }))
    
def step_card_inline(request,card_type,
                     template_name="application/step_card.html"):
    form = CustomerCardForm()
    is_customer = False
    if card_type == APP_TYPE_CARD_EMP:
        title = u"電腦出入管制卡申請單(員工專用)"
        applicant_info_inline = employee_info_inline(request)
        device_info_inline_html = device_info_inline(request)
    
    elif card_type == APP_TYPE_CARD_CUSTOMER_ONSITE:
        title = u"電腦出入管制卡申請單(駐廠客戶專用)"
        applicant_info_inline = customer_info_inline(request)
        device_info_inline_html = device_info_inline(request,show_owner=False)
        
    elif card_type == APP_TYPE_CARD_CUSTOMER:
        title = u"電腦出入管制卡申請單(客戶專用)"
        applicant_info_inline = customer_info_inline(request)
        device_info_inline_html = device_info_inline(request,show_owner=False)
        is_customer = True
    
    return render_to_string(template_name,RequestContext(request, {
        "title":title,
        "form":form,
        "is_customer":is_customer,
        "applicant_info_inline":applicant_info_inline,
        "device_info_inline":device_info_inline_html,
        "comment_inline":comment_inline(request),
        "attachment_upload_inline":attachment_upload_inline(request),
    }))
    
def step_done(request,data,template_name="application/step_done.html"):

    return render_to_string(template_name,RequestContext(request, {
        "data":data,
    }))
    
@transaction.commit_on_success
def app_wizard(request,step_index):
    if step_index == '1':
        save_post_to_session(request,'step2')
        return render_to_response('application/step1_choose_type.html')
        
    elif step_index == '2':
        save_post_to_session(request,'step1')
        grade_list = EmpGrade.objects.all()
        postion_list =EmpPostion.objects.all()
        if request.method=='POST':
            app_type = request.POST.get('app_type','')
            if app_type=='1' :
                pass
            if app_type=='2' :
                return render_to_response('application/step2_card_emp.html',locals())
            if app_type=='3' :
                return render_to_response('application/step2_card_customer_onsite.html',locals())
            if app_type=='4' :
                return render_to_response('application/step2_card_customer.html',locals())
    elif step_index == '3':
        app_type = request.session['step1'].get('app_type','')
        if app_type =='1':
            app_type_db = 'carry'
            #TODO:攜入攜出申請單的class_type判斷
        elif app_type in ['2','3','4']:
            app_type_db = 'card'
                
            if app_type =='2':
                class_type ='card_emp'
            elif app_type =='3':
                class_type = 'card_customer_onsite'
                #route_name = 'card_customer_onsite'
            elif app_type =='4':
                class_type = 'card_customer'
                #route_name = 'card_customer'
            route_name = class_type
            
            image = request.FILES['id_image']
            print image.name
    
            app = create_application(app_type=app_type_db,class_type=class_type,
                                     request=request)
            return HttpResponse(u'<h1>單號:'+app.app_id+u'提交成功</h1><br><h2>請等待簽核!</h2>')
            
def app_wizard_json(request,step_index):
    session_key = 'step'+ step_index
    return JsonResponse(request.session.get(session_key,''))

@login_required
def app_list(request,template_name="application/sign_list.html"):
    
    app_list =[]
    try:
        page = request.GET.get('page')
        user = request.user
        #from django.db import connection, transaction
        
        not_status = [
            APP_STATUS_SUBMIT,
            APP_STATUS_CLOSED,
            APP_STATUS_REJECTED,
            APP_STATUS_IN_GUARD_CHECK,
            APP_STATUS_OUT_GUARD_CHECK
        ]
        
        app_basic = ApplicationBase.objects.exclude(status__name__in = not_status)
        
        for app in app_basic:
            #if app.has_signed_perm(user=user):
            app_list.append([
                app.created_date, 
                app.number,
                app.app_name,
                app.submit.employee.name,
                app.submit.employee.department.name,
                app.get_user_name(),
            ])
        
        paginator = Paginator(app_list,8)
        try:
            show_apps = paginator.page(page)
        except PageNotAnInteger:
            show_apps = paginator.page(1)
        except (EmptyPage,InvalidPage):
            show_apps = paginator.page(paginator.num_pages)
        
        #print app_list
        
    except Exception,e:
        print e
    
    ##if request.GET:
    #   reponse = {'content':app_list}
    #    return JsonResponse(reponse)
    #else:
    #    return render_to_response('application/sign_list.html',locals(),
    #            context_instance=RequestContext(request))

    return render_to_response(template_name,RequestContext(request,{
        "app_list":show_apps,
    }))
    
    """
    try:
        user = request.user
        role_list = user.role_set.all()
        print role_list
        app_status_list =[]
        for role in role_list:
            try:
                app_status = AppStatus.objects.get(name=role.name)
                if app_status:
                    app_status_list.append(app_status)
            except Exception,e:
                print e
            
        app_status_id_list=[]
        for app_status in app_status_list:
            app_status_id_list.append(app_status.id)
        
        # 獲取查詢參數
        page = int(request.GET.get('page',1))
        order = request.GET.get('order',1)
        asc = request.GET.get('asc','false')
        per_page_num = 5
        col_name_list = {'1':'a.created_date','2':'a.app_id','3':'a.class_type',
                         '4':'u.first_name','5':'','6':'c.name,b.name'}
        col_name = col_name_list.get(order,'1')
             
        if asc == 'true':
            asc = 'ASC'
        else:
            asc = 'DESC'
        order_by = ''.join([col_name,' ',asc])  #構造SQL語句中order by子語句
        
        if len(app_status_id_list)>1:
            in_sub = 'IN'
        else:
            in_sub = '='
            app_status_id_list = app_status_id_list[0]
            
        from django.db import connection, transaction
        cursor = connection.cursor()
        sql = ''.join(['SELECT COUNT(*) FROM r_application a WHERE a.status_id ',in_sub,' %s ;'])
        #TODO:對申請人的部門進行判斷...
        cursor.execute(sql,[app_status_id_list])

        query_result = cursor.fetchall()
        app_count = query_result[0][0]
        total_page = app_count/per_page_num
        if app_count%per_page_num:
            total_page +=1
        
        if page>total_page or page<1:
            page = 1
        
        offset = (page-1)*per_page_num

        sql =   ''.join(['''
                SELECT a.created_date,a.app_id,a.class_type,u.first_name,b.name,c.name
                FROM r_application a
                LEFT JOIN auth_user u ON a.submit_by_id = u.id 
                LEFT JOIN r_application_card b ON a.app_id=b.application_id
                LEFT JOIN r_application_in_out c ON a.app_id=c.application_id
                WHERE a.status_id ''',in_sub,''' %s
                ORDER BY ''',order_by,' LIMIT %s,%s'])
        cursor.execute(sql,[app_status_id_list,offset,per_page_num])
        

        app_list = cursor.fetchall()
        
        #app_list = Application.objects.filter(status__in=app_status_list)\
        #            .extra(select={'card_name':'r_application_card.name'},#'carry_name':'r_application_in_out.name'
        #                   tables=['r_application_card'],#,'r_application_in_out'
        #                   where=['r_application.app_id=r_application_card.application_id']#'r_application.app_id=r_application_in_out.application_id'
        #                          )
        print app_list
        
    except Exception,e:
        print e
    
    if request.GET:
        reponse = {'page':page,'total_page':total_page,'content':app_list}
        return JsonResponse(reponse)
    else:
        return render_to_response('application/sign_list.html',locals(),
                context_instance=RequestContext(request))
    """

def app_download(request, app_id, show_indexes=False):
    """
    下載攜入攜出申請單PDF檔
    """
    path = app_id +'.pdf'
    document_root = settings.APP_PDF_ROOT
    return download_view(request, path, document_root, show_indexes=False)
    
def detail_comment_inline(request,app,):
    return render_to_string(template_name,RequestContext(request, {
        "app":app,
    }))
    
def detail_emp_inline(request,app,template_name="application/app_detail_emp_inline.html"):
    return render_to_string(template_name,RequestContext(request, {
        "app":app,
    }))
    
def detail_customer_inline(request,app,template_name="application/app_detail_customer_inline.html"):
    return render_to_string(template_name,RequestContext(request, {
        "app":app,
    }))
    
def detail_device_inline(request,app,template_name="application/app_detail_device_inline.html"):
    return render_to_string(template_name,RequestContext(request, {
        "app":app,
    }))
    
def detail_app_carry_applicant_inline(request,app):
    pass
    
def detail_app_carry_inline(request):
    pass
    
def detail_app_inline(request,app):
    is_customer = False

    if app.type == APP_TYPE_CARD_EMP:
        template_name='application/app_card_detail.html'
        app_card = ApplicationCard.objects.get(application=app)
        detail_applicant_inline_html = detail_emp_inline(request,app_card)
        detail_device_inline_html = detail_device_inline(request,app_card)
    elif app.type == APP_TYPE_CARD_CUSTOMER:
        template_name='application/app_card_detail.html'
        app_card = ApplicationCard.objects.get(application=app)
        is_customer = True
        detail_applicant_inline_html = detail_customer_inline(request,app_card)
        detail_device_inline_html = detail_device_inline(request,app_card)
    elif app.type == APP_TYPE_CARD_CUSTOMER_ONSITE:
        template_name='application/app_card_detail.html'
        app_card = ApplicationCard.objects.get(application=app)
        detail_applicant_inline_html = detail_customer_inline(request,app_card)
        detail_device_inline_html = detail_device_inline(request,app_card)
        
    elif app.type in [APP_TYPE_CARRY_INOUT,APP_TYPE_CARRY_IN]:
        template_name='application/app_carry_detail.html'
        #app_carry_in = ApplicationIn.objects.get(application=app)
        app_carry = app.get_carry_object()
        detail_device_inline_html = detail_device_inline(request,app_carry["in"])
        detail_customer_inline_html = detail_customer_inline(request,app_carry["in"])
        detail_emp_inline_html = detail_emp_inline(request,app_carry["in"])
        
    elif app.type == APP_TYPE_CARRY_OUT:
        template_name='application/app_carry_detail.html'
        app_carry = app.get_carry_object()
        print app_carry['out']
        detail_device_inline_html = detail_device_inline(request,app_carry["out"])
        detail_customer_inline_html = detail_customer_inline(request,app_carry["out"])
        detail_emp_inline_html = detail_emp_inline(request,app_carry["out"])
        
    if app.type in [APP_TYPE_CARD_EMP,APP_TYPE_CARD_CUSTOMER,APP_TYPE_CARD_CUSTOMER_ONSITE]:
        return render_to_string(template_name,RequestContext(request, {
            "is_customer":is_customer,
            "detail_applicant_inline":detail_applicant_inline_html,
            "detail_device_inline":detail_device_inline_html,
            "app_card":app_card,
        }))
    else:
        return render_to_string(template_name,RequestContext(request, {
            #"detail_applicant_inline":detail_applicant_inline_html,
            "detail_device_inline":detail_device_inline_html,
            "detail_customer_inline":detail_customer_inline_html,
            "detail_emp_inline":detail_emp_inline_html,
            "app":app,
            "app_carry":app_carry,
        }))

def app_unsigned_inline(request):
    pass

def carry_detail_inline(app,template_name = "application/detail_carry.html"):
    
    return render_to_string(template_name,RequestContext(request, {
            #"detail_applicant_inline":detail_applicant_inline_html,
            "detail_device_inline":detail_device_inline_html,
            "detail_customer_inline":detail_customer_inline_html,
            "detail_emp_inline":detail_emp_inline_html,
            "app":app,
        }))

@login_required
def app_detail(request,app_id,template_name="application/sign_detail.html"):
    try:
        
        app_base = ApplicationBase.objects.get(number=app_id)
        app = app_base.get_app_detail_cls()
        
        if app_base.type_code.startswith("CARRY"):
            detail_template = 'application/detail_carry.html'
        
        detail_app_html = detail_app_inline(request,app)
        
        app_history = ApplicationHistory.objects.filter(application=app)
        
        print app_history
        
        if app.status.name == APP_STATUS_IN_GUARD_CHECK:
            app_status = "guard_in"
        elif app.status.name == APP_STATUS_OUT_GUARD_CHECK:
            app_status = "guard_out"
        elif app.status.name == APP_STATUS_MAKE_CARD:
            app_status = "make_card"
        else:
            app_status = "other_status"
            
        unsigner_list = app.get_unsigner_list()
        
        has_signed_perm = app.has_signed_perm(user=request.user)
        #print unsigner_list
        #print unicode(app.get_current_signer()[0])
        #SignedHistory.objects.filter(application=app).order_by('date')
        #sh_list = SignedHistory.objects.get_history(app=app)
        #print sh_list
    except Exception,e :
        print e

    return render_to_response(template_name,RequestContext(request,{
        "detail_template":detail_template,
        #"detail_app_html":detail_app_html,
        #"app_history":app_history,
        #"unsigner_list":unsigner_list,
        "app":app,
        #"app_status":app_status,
        #"has_signed_perm":has_signed_perm,
        #'ROUTE_ACTION_REJECT':ROUTE_ACTION_REJECT,
    }))

def app_signed_view(request,app_id):
    status = "failure"
    
    if request.POST:
        action = request.POST.get('action','').lower()
        comment = request.POST.get('comment','')
        if action == 'agree':
            action = ROUTE_ACTION_AGREE
        elif action == 'reject': 
            action = ROUTE_ACTION_REJECT
        elif action =='done':
            action = ROUTE_ACTION_DONE

        app_query = ApplicationBase.objects.filter(number=app_id)
        if app_query:
            signed = app_query[0].do_signed(user=request.user,
                         action = action,
                         comment= comment,
            )
            if signed :
                # 發送郵件通知
                app_signed_signal.send({'request':request,'app':app_query[0]})
                status = "success"
                

    result = simplejson.dumps({
        "status":status,
        #"html":add_signer_inline(request,signer_form),
    }, cls=LazyEncoder)
    return HttpResponse(result,mimetype='application/json')

@login_required
def app_search(request,template_name="application/app_search.html"):
    app_list =[]
    try:
        user = request.user
        #from django.db import connection, transaction
        q = request.GET.get('q','')
        page = request.GET.get('page')
        if request.GET:
            filters = Q(number__icontains=q)
            if user.has_perm('application.view_all_status'):
                pass
            elif user.has_perm('application.view_guard_status'):
                filters &= Q(status__name__in=[APP_STATUS_IN_GUARD_CHECK,APP_STATUS_OUT_GUARD_CHECK])|Q(submit=user)
            else: 
                filters &= Q(submit=user)
                
            app_basic = ApplicationBase.objects.filter(filters)
            
            for app in app_basic:
                app_list.append([
                    app.created_date, 
                    app.number,
                    app.get_type_display(),
                    app.submit.employee.name,
                    app.submit.employee.department.name,
                    app.get_user_name(),
                    app.status.get_display_name_display(),
                    ]
                )
                
        paginator = Paginator(app_list,8)
        try:
            show_apps = paginator.page(page)
        except PageNotAnInteger:
            show_apps = paginator.page(1)
        except (EmptyPage,InvalidPage):
            show_apps = paginator.page(paginator.num_pages)
        
    except Exception,e:
        print e
        
    return render_to_response(template_name,RequestContext(request,{
        "app_list":show_apps,
        "q":q,
    }))

def my_app(request):
    pass
    
def view_test(request):
    #from  django.shortcuts import render_to_response,  get_object_or_404
    
    #user  =  get_object_or_404  (User, username='h7104941')
    from core.utils import set_message_cookie
    from .forms import TestForm
    
    if request.POST:
        print request.POST
        form = TestForm(request.POST)
        #form._errors =[]
        if form.is_valid():
            t = form.save()
        else:
            form._errors ={}
            t = form.save()
        

    else:
        form = TestForm()
        
    t = get_template('application/test_file.html')
    c=RequestContext(request,locals())
    
    response =  HttpResponse(t.render(c))
    return response

def delete_pic(request):
    pic_instance = Test.objects.get(id=request.POST['id'])
    from django.core.files.storage import default_storage as ds
    pic_path = pic_instance.image.path
    ds.delete(pic_path)
    pic_instance.delete()
    return HttpResponse('OK')
    
def view_form(request,template_name="application/test_form.html"):
    if request.method=="POST":
        contact_form = ContactForm(request.POST)
    else:
        contact_form = ContactForm()
        
    return render_to_response(template_name,RequestContext(request,{'form':contact_form}))
    