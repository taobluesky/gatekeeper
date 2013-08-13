# -*- coding: utf-8 -*-
#python imports
import uuid

# django imports
from django import forms

#gk import
from .models import ApplicationBase
from .models import ApplicationCard
from .models import ApplicationIn
from .models import ApplicationOut
from .models import ApplicationDevice
from .models import RouteHeader
from .models import generate_appid
from gatekeeper.account.models import Employee
from .settings import APP_TYPE_CARRY_INOUT
from .settings import APP_TYPE_CARRY_IN
from .settings import APP_TYPE_CARRY_OUT
from .settings import APP_TYPE_CARD_EMP
from .settings import APP_TYPE_CARD_CUSTOMER
from .settings import APP_TYPE_CARD_CUSTOMER_ONSITE
from .settings import APP_STATUS_SUBMIT
from .settings import APPLICANT_TYPE_CUSTOMER
from .settings import APPLICANT_TYPE_EMPLOYEE
from .settings import APP_TYPE_ROUTE_NAME

def get_uuid_str():
    return str(uuid.uuid4())
    
def create_app_basic(request,app_type):
    """
    創建申請單的基本信息 application_basic Object
    app_type:
        "CARRY_INOUT","CARRY_IN","CARRY_OUT","CARD_EMP","CARD_CUSTOMER","CARD_CUSTOMER_ONSITE"
    """
    app_type_list = ("CARRY_INOUT","CARRY_IN","CARRY_OUT","CARD_EMP","CARD_CUSTOMER","CARD_CUSTOMER_ONSITE")
    route_name = app_type_str = app_type_list[app_type]
    prefix = app_type_str.split('_')[0]
    number = generate_appid(prefix=prefix)
    select_route = RouteHeader.objects.get(route_name=route_name)
    
    app_basic = ApplicationBase(number=number,
                                 type=app_type,
                                 route=select_route,
                                 submit=request.user,
                                )
    app_basic.save()
    return app_basic
    
def save_application_carry_util(request,device_form,carry_form):
    """
    保存攜入攜出申請單數據
    """
    type_code = 'CARRY_'
    
    carry_in = carry_form.cleaned_data["carry_in"]
    carry_out = carry_form.cleaned_data["carry_out"]
    if carry_in and carry_out :
        type_code += 'INOUT_'
    elif carry_in :
        type_code += 'IN_'
    elif carry_out:
        type_code += 'OUT_'
    applicant_type = carry_form.cleaned_data["applicant_type"]
    if applicant_type == APPLICANT_TYPE_CUSTOMER:
        type_code += 'CUSTOMER'
    elif applicant_type == APPLICANT_TYPE_EMPLOYEE:
        type_code += 'EMP'
    
    app_number = generate_appid(prefix='CARRY')
    #route = _get_route(type_code)
    app_base = ApplicationBase(
        number = app_number,
        type_code = type_code,
        #route = route,
        submit = request.user,
    )
    app_base.save()
    device = device_form.save()
    app_carry = carry_form.save(commit=False)
    app_carry.application = app_base
    app_carry.device = device
    app_carry.save()

    
def create_card_emp(request,device_form,employee_form,comment_form,attachment_form):
    """
    創建管製卡(員工)
    """
    app_basic = create_app_basic(request,app_type=APP_TYPE_CARD_EMP)
    device = get_device(device_form)
    
    app_card = ApplicationCard(application=app_basic,
        comment=comment_form.cleaned_data["comment"],
        device=device,
        emp_no=employee_form.cleaned_data["emp_no"],
        emp_name=employee_form.cleaned_data["emp_name"],
        department=employee_form.cleaned_data["department"],
        grade=employee_form.cleaned_data["grade"],
        position=employee_form.cleaned_data["position"],
        extension=employee_form.cleaned_data["extension"],
        emp_telephone=employee_form.cleaned_data["emp_telephone"],
        #id_type=employee_form.cleaned_data["id_type"],
        id_image=attachment_form.cleaned_data["id_image"],
        promise_image=attachment_form.cleaned_data["promise_image"],
    )
    app_card.save()
    return app_basic
    
def create_card_customer(request,device_form,customer_form,customer_card_form,comment_form,attachment_form):
    """
    創建管製卡(客戶)
    """
    app_basic = create_app_basic(request,app_type=APP_TYPE_CARD_CUSTOMER)
    device = get_device(device_form)
    app_card = ApplicationCard(application = app_basic,
        comment=comment_form.cleaned_data["comment"],
        start_date = customer_card_form.cleaned_data["start_date"],
        end_date = customer_card_form.cleaned_data["end_date"],
        device = device,
        customer_name = customer_form.cleaned_data["customer_name"],
        customer_company = customer_form.cleaned_data["customer_company"],
        id_type = customer_form.cleaned_data["id_type"],
        id_no = customer_form.cleaned_data["id_no"],
        customer_telephone=customer_form.cleaned_data["customer_telephone"],
        id_image=attachment_form.cleaned_data["id_image"],
        promise_image=attachment_form.cleaned_data["promise_image"],
    )
    app_card.save()
    return app_basic

def create_card_customer_onsite(request,device_form,customer_form,comment_form,attachment_form):
    """
    創建管製卡(駐廠客戶)
    """
    app_basic = create_app_basic(request,app_type=APP_TYPE_CARD_CUSTOMER_ONSITE)
    device = get_device(device_form)
    app_card = ApplicationCard(application = app_basic,
        comment = comment_form.cleaned_data["comment"],
        device = device,
        customer_name = customer_form.cleaned_data["customer_name"],
        customer_company = customer_form.cleaned_data["customer_company"],
        id_type = customer_form.cleaned_data["id_type"],
        id_no = customer_form.cleaned_data["id_no"],
        customer_telephone=customer_form.cleaned_data["customer_telephone"],
        id_image=attachment_form.cleaned_data["id_image"],
        promise_image=attachment_form.cleaned_data["promise_image"],
    )
    app_card.save()
    return app_basic
    
def create_carry_inout(request,carry_form,customer_form,receiver_form,employee_form,device_form,attachment_form):
    """
    創建攜入攜出申請
    """
    device = get_device(device_form)
    data = {}
    if carry_form.cleaned_data["applicant_type"] == APPLICANT_TYPE_CUSTOMER :
        print 'APPLICANT_TYPE_CUSTOMER'
        if customer_form.is_valid() and receiver_form.is_valid():
            print "form okay."
            data.update({
                "emp_no":receiver_form.cleaned_data["emp_no"],
                "emp_name":receiver_form.cleaned_data["emp_name"],
                "department":receiver_form.cleaned_data["department"],
                "grade": receiver_form.cleaned_data["grade"],
                "position" : receiver_form.cleaned_data["position"],
                "extension" : receiver_form.cleaned_data["extension"],
                "emp_telephone": receiver_form.cleaned_data["emp_telephone"],
                "customer_company" : customer_form.cleaned_data["customer_company"],
                "customer_name" : customer_form.cleaned_data["customer_name"],
                "customer_telephone" :customer_form.cleaned_data["customer_telephone"],
                "id_type" :customer_form.cleaned_data["id_type"],
                "id_no" :customer_form.cleaned_data["id_no"],
                "id_image" :attachment_form.cleaned_data["id_image"],
                "promise_image" :attachment_form.cleaned_data["promise_image"],
            })
        else:
            return
    elif carry_form.cleaned_data["applicant_type"] == APPLICANT_TYPE_EMPLOYEE :
        print 'APPLICANT_TYPE_EMPLOYEE'
        if employee_form.is_valid():
            data.update({
                "emp_no":employee_form.cleaned_data["emp_no"],
                "emp_name":employee_form.cleaned_data["emp_name"],
                "department":employee_form.cleaned_data["department"],
                "grade": employee_form.cleaned_data["grade"],
                "position" : employee_form.cleaned_data["position"],
                "extension" : employee_form.cleaned_data["extension"],
                "emp_telephone": employee_form.cleaned_data["emp_telephone"],
            })
        else:
            return
    
    carry_in = carry_form.cleaned_data["carry_in"]
    carry_out = carry_form.cleaned_data["carry_out"]
    
    # 創建data dict,并保存至DB
    if carry_in:
        data.update({
            "in_comment" : carry_form.cleaned_data["in_comment"],
            "in_date" : carry_form.cleaned_data["in_date"],
            "in_dest" : carry_form.cleaned_data["in_dest"],
            "device" : device,
            "id_image" : attachment_form.cleaned_data["id_image"],
            "promise_image" : attachment_form.cleaned_data["promise_image"],
        })
        if carry_out:
            app_type =  APP_TYPE_CARRY_INOUT
            data.update({"union_out":True})
        else:   
            app_type =  APP_TYPE_CARRY_IN
            
        app_basic = create_app_basic(request,app_type=app_type)
        data.update({"application":app_basic})
        print data
        app_carry_in = ApplicationIn(**data)
        app_carry_in.save()
    if carry_out:
        data.update({
            "out_comment" : carry_form.cleaned_data["out_comment"],
            "out_date" : carry_form.cleaned_data["out_date"],
            "out_dest" : carry_form.cleaned_data["out_dest"],
            "device" : device,
            "id_image" : attachment_form.cleaned_data["id_image"],
            "promise_image" : attachment_form.cleaned_data["promise_image"],
        })
        if not carry_in:
            app_type = APP_TYPE_CARRY_OUT
            app_basic = create_app_basic(request,app_type=app_type)
            data.update({"application":app_basic})
        else:
            keys =["in_comment","in_date","in_dest","union_out"]
            for key in keys:
                if key in data:
                    del data[key]
        print data
        app_carry_out = ApplicationOut(**data)
        app_carry_out.save()

    return app_basic
    
def get_device(device_form):
    try:
        app_device = ApplicationDevice.objects.get(sn=device_form.cleaned_data["sn"])
    except Exception,e:
        app_device = ApplicationDevice(owner=device_form.cleaned_data["owner"],
            manufacturer=device_form.cleaned_data["manufacturer"],
            model_no=device_form.cleaned_data["model_no"],
            color=device_form.cleaned_data["color"],
            sn=device_form.cleaned_data["sn"],
            lan_mac=device_form.cleaned_data["lan_mac"],
            wifi_mac=device_form.cleaned_data["wifi_mac"],
        )
        app_device.save()
    return app_device
    

    