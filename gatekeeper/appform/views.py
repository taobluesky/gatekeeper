from django import forms
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import datetime
# app specific files

from models import *
from forms import *
import time,re

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.db import transaction
from django.http import HttpResponse
from django.utils import simplejson
import json

NOW = time.localtime()
DATENOW = time.strftime('%Y-%m-%d',NOW)
TIMENOW = time.strftime('%H:%M:%S',NOW)
DATETIMENOW = time.strftime('%Y-%m-%d %H:%M:%S',NOW)
    
#响应json数据
class JsonResponse(HttpResponse):
    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = simplejson.dumps(object)
        super(JsonResponse, self).__init__(content, mimetype='application/json')

def indexpage(request):
    return render_to_response('base.html')
    
def create(request):
    return render_to_response('appform/wizard_base.html')

#取得session内容 (已經廢棄)
def get_wizard_session(request):
    wizard_session = request.session.get('wizard',[])
    #print wizard_session
    if wizard_session :
        return wizard_session
    else:
        request.session['wizard']={}
        return request.session['wizard']

#返回json數據
def wizard_json(request,next_step_idx):
    session_key = 'step'+ next_step_idx
    return JsonResponse(request.session.get(session_key,''))

#存儲post data到session
def save_post_to_session(request,stepnumber):
    keylist = request.POST.keys()
    step_session ={}
    for key in keylist:
        step_session[key] = request.POST[key]
    request.session[stepnumber] = step_session
    #print stepnumber + str(request.session[stepnumber])
    
def create_wizard(request,next_step_idx):
    #print 'next_step_idx ='+ next_step_idx
    #print 'cur_step_idx ='+ request.POST.get('cur_step_idx','')
    #保存post中表單信息
    cur_step_idx = request.POST.get('cur_step_idx','')
    if cur_step_idx in ['1','2','3','4']:
        stepnumber = 'step' + cur_step_idx
        save_post_to_session(request,stepnumber)
        
    #顯示表單
    if next_step_idx =='1':
        return render_to_response('wizard_step1.html')#,context_instance=RequestContext(request)
    elif next_step_idx =='2':
        return render_to_response('wizard_step2.html')
    elif next_step_idx =='3':
        return render_to_response('wizard_step3.html')
    elif next_step_idx =='4':
        #判斷申請類型
        if request.session['step1']['app_type'] =='1':
            return render_to_response('wizard_step4.html')
        else:
            return render_to_response('wizard_step4_1.html')
    elif next_step_idx =='5':
        #存儲表單數據
        device_info = request.session['step2']
        #print device_info
        #設備信息存儲
        dev = Device(owner = device_info['owner'],
                     manufacturer = device_info['manufacturer'],
                     model_no = device_info['model_no'],
                     color = device_info['color'],
                     sn = device_info['sn'],
                     lan_mac = device_info['lan_mac'],
                     wifi_mac = device_info['wifi_mac'])
        dev.save()
        
        #申請人信息
        applicant_info = request.session['step3']
        app_type = request.session['step1']['app_type']
        if app_type in ['1','4','5']:
            # isguest = '1':來訪人或者客戶  '2':集團員工
            if applicant_info['isguest'] =='1':
                guest = Guest(name = applicant_info['name'],
                              company = applicant_info['company'],
                              phone = applicant_info['phone'],
                              identify_type = applicant_info['identify_type'],
                              identify_no = applicant_info['identify_no'])
                guest.save()
                emp_no = applicant_info['emp_no_1']
                user = User.objects.get(emp_no=emp_no)
        if app_type in['1','3']:
            if applicant_info['isguest'] =='2':
                guest = None
                emp_no = applicant_info['emp_no_2']
                user = User.objects.get(emp_no=emp_no)
        
        
        #存儲主申請單
        app_no = generate_appno()#產生單號
        app = Application(app_no = app_no,
                          guest = guest,
                          device = dev)
        app.save()
        #存儲詳細申請單
        app_detail = request.session['step4']
        if app_type =='1':
            if app_detail.get('carry_in','') =='1':
                app_in = App_Detail(application =app,
                                    app_type = 1,
                                    applicant = user,
                                    app_reason = app_detail['app_reason_1'],
                                    requested_dt = app_detail['requested_dt_1'],
                                    device_dest = app_detail['device_dest_1']
                                    )
                app_in.save()
            if app_detail.get('carry_out','') =='1':
                app_out  = App_Detail(application =app,
                                      app_type = 2,
                                      applicant = user,
                                      app_reason = app_detail['app_reason_2'],
                                      requested_dt = app_detail['requested_dt_2'],
                                      device_dest = app_detail['device_dest_2']
                                      )
                app_out.save()
        elif app_type in ['3','4','5']:
            card_app = App_Detail(application = app,
                                  app_type = int(app_type),
                                  applicant = user,
                                  app_reason = app_detail['app_reason'],
                                  requested_dt = app_detail['requested_dt']
                                  #device_dest = app_detail['device_dest_1']
                                  )
            card_app.save()

        #todo 清除seesion數據~
        return HttpResponse('申請已經提交！')
        
def create_app(request):
    apptypeform = AppTypeForm()
    return render_to_response('base.html',{'form':apptypeform})

##########################################################
# 这个是通过form模块进行编写视图，后续不使用此种方式。
##########################################################
def wizard__(request,step_index,step_current):
    print 'postdata =' + str(request.POST)
    
    #新建頁面
    if step_current=='0' and step_index=='1':
        step1_session = request.session.get('step1','')
        if step1_session:
            apptypeform = AppTypeForm(step1_session)
        else:
            apptypeform = AppTypeForm()
        return render_to_response('appform/step1.html',{'form':apptypeform})
    #Step1頁面
    if step_current=='1':
        #if request.method=='POST':
        apptypeform = AppTypeForm(request.POST)
        if apptypeform.is_valid():
            #print apptypeform.cleaned_data
            save_post_to_session(request,'step1')
            device_form = DeviceForm()
            emp_form = EmpInfoForm()
            return render_to_response('appform/step2.html',{'device_form':device_form,'emp_form':emp_form})
        else:
            return render_to_response('appform/step1.html',{'form':apptypeform})
            
    #Step2頁面  
    if step_current=='2':
        if step_index=='1':
            pass

@transaction.commit_on_success
def wizard(request,step_index,step_current):
    #保存post數據到session中
    if step_current in ['1','2']:
        print 'step_current=',step_current
        stepnumber = ''.join(['step' , step_current])
        save_post_to_session(request,stepnumber)
        
    if step_index=='1':
        return render_to_response('appform/step1.html')
    elif step_index=='2':
        if request.method=='POST':
            app_type = request.POST.get('app_type','')
        if app_type=='3':
            return render_to_response('appform/step2_card_emp.html')
        
    elif step_index=='3':
        app_type = request.session['step1']['app_type']#3.管製卡（員工）
        if app_type =='3':
            device = Device.objects.create_device(owner=request.POST['owner'],manufacturer=request.POST['manufacturer'],
                                                  model_no=request.POST['model_no'],color=request.POST['color'],
                                                  sn=request.POST['sn'],
                                                  lan_mac=request.POST['lan_mac'],wifi_mac=request.POST['wifi_mac'])
            #生成單號
            app_no = generate_appno()
            app = Application(app_no = app_no,guest = None,device = device)
            app.save()
            user = User.objects.get(username=request.POST['emp_no'])
            card_app = App_Detail(application = app,
                                  app_type = 3,
                                  applicant = user,
                                  app_reason = request.POST['reason'],
                                  requested_dt = time.strftime('%Y-%m-%d',NOW)
                                  #device_dest = app_detail['device_dest_1']
                                  )
            card_app.save()
            return render_to_response('appform/done.html')

def test_select(request):
    query_set = TestModel.objects.all()
    select = TestForm(query_set)
    return render_to_response('appform/test_select.html',{'select':select})
    
#暫時採用此規則生成單號~
def generate_appno():
    dt = time.strftime('%Y%m%d%H',NOW)
    app_no = 'TJ-' + dt
    try:
        data = Application.objects.filter(app_no__startswith=app_no).order_by('-app_no')[0].app_no
        app_no = 'TJ-' + dt + '-' + str(int(data[-4:])+1).zfill(4)
    except Application.DoesNotExist:
        app_no = app_no + '-0001'
    except IndexError:
        app_no = app_no + '-0001'
    
    return app_no
    