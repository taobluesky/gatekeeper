#-*-coding:utf-8-*-

#python imports
import os
import re

#django imports
from django import forms
from django.forms import ModelForm
from django.forms.widgets import ClearableFileInput
from django.utils.translation import ugettext_lazy as _
from models import *
from django.core.urlresolvers import reverse

#gatekeeper imports
from gatekeeper.account.models import Organization
from gatekeeper.account.models import Employee
from .settings import MANUFACTURER_CHOICES,COLOR_CHOICES,OWNER_CHOICES
from .models import ApplicationCarry,ApplicationCard,ApplicationIn,ApplicationOut,ApplicationDevice
from .settings import APP_TYPE_CARRY_INOUT
from .settings import APP_TYPE_CARD_EMP,APP_TYPE_CARD_CUSTOMER,APP_TYPE_CARD_CUSTOMER_ONSITE
from .settings import CARRY_APPLICANT_TYPE_CHOICES,APPLICANT_TYPE_CUSTOMER,APPLICANT_TYPE_EMPLOYEE
from .settings import OWNER_CHOICES_PERSONAL
from .utils import get_uuid_str
from .fields import MacField

# 3rd pack imports
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput

def _clean_image(cleaned_data):
    """
    攜入攜出 及 管製卡
    驗證clean函數中: 修改id_image 和 promise_image 的文件名
    """
    id_image = cleaned_data.get("id_image")
    if id_image :
        file_ext = os.path.splitext(id_image.name)[1]
        file_name = get_uuid_str()
        id_image.name = ''.join([file_name,file_ext])
    promise_image = cleaned_data.get("promise_image")
    if promise_image:
        file_ext = os.path.splitext(promise_image.name)[1]
        file_name = get_uuid_str()
        promise_image.name = ''.join([file_name,file_ext])
        
class ApplicationCarryForm(ModelForm):
    """
    攜入攜出申請單 表單
    """
    carry_in = forms.BooleanField(label=_(u'申請攜入'),required=False)
    carry_out = forms.BooleanField(label=_(u'申請攜出'),required=False)
    applicant_type = forms.ChoiceField(
        label=_(u'申請類型'),
        choices=CARRY_APPLICANT_TYPE_CHOICES
    )
    emp_no = forms.CharField(
        label = _(u"工號"),
        max_length = 20,
        widget=BootstrapUneditableInput(),
        initial=u''
    )
    emp_name = forms.CharField(
        label=_(u"姓名"),
        max_length=50,
        widget=BootstrapUneditableInput(),
        initial=u''
    )
    emp_department = forms.CharField(
        label=_(u"單位"),
        max_length=255,
        widget=BootstrapUneditableInput(),
        initial=u''
    )
    id_image = forms.ImageField(
        label=_(u'證件影印'),
        widget = ClearableFileInput(attrs={"accept":"image/*"})
    )

    def __init__(self,data=None,files=None,user = None,*args,**kwargs):
        """
        根據用戶提交的數據動態設置field的required值,
        并去除不需要驗證的字段以免保存無關字段.
        更多細節請查看 django.forms 源代碼...
        """
        # 強制表單申請人為user信息
        fore_data ={}
        if user:
            emp = Employee.objects.get(emp_no = user.employee.emp_no)
            fore_data = {
                "emp_no":emp.emp_no,
                "emp_name":emp.name,
                #"notes_mail":emp.notes_mail,
                "emp_extension":emp.extension,
                "emp_telephone":emp.telephone,
                #"emp_grade":emp.grade,
                "emp_position":emp.position,
                "emp_department":emp.department.name,
            }
            if data:
                # 使表單申請人信息可更改以下三個欄位
                fore_data.pop("emp_extension")
                fore_data.pop("emp_telephone")
                fore_data.pop("emp_position")
                data.update(fore_data)
            else:
                initial = fore_data
            
        super(ApplicationCarryForm, self).__init__(data,files,initial=fore_data,*args, **kwargs)
        
        id_template_url =reverse('gk_download', kwargs={'path':'id_template.pdf'})
        self.fields["id_image"].help_text=_(u"影印證件（含簽名），上傳掃描檔。<i class='icon-download-alt'></i><a href='%s'>下載模板</a>") % id_template_url
        # 根據用戶提交的申請類型,判定必須的欄位
        if data:
            applicant_type = self.fields["applicant_type"].clean(data.get("applicant_type"))
            if applicant_type == APPLICANT_TYPE_EMPLOYEE:
                is_customer = False
                self.fields["customer_company"].required = is_customer
                self.fields["customer_name"].required = is_customer
                self.fields["customer_telephone"].required = is_customer
                self.fields["customer_id_type"].required = is_customer
                self.fields["customer_id_no"].required = is_customer
                self.data["customer_company"] =''
                self.data["customer_name"] =''
                self.data["customer_telephone"] =''
                self.data["customer_id_type"] = 0
                self.data["customer_id_no"] = ''
                
            carry_in=self.fields["carry_in"].clean(data.get("carry_in"))
            if not carry_in :
                self.fields["in_comment"].required=carry_in
                self.fields["in_date"].required=carry_in
                self.fields["in_dest"].required=carry_in
                self.data["in_comment"] =''
                self.data["in_date"] =''
                self.data["in_dest"] =''
            carry_out=self.fields["carry_out"].clean(data.get("carry_out"))
            if not carry_out:
                self.fields["out_comment"].required=carry_out
                self.fields["out_date"].required=carry_out
                self.fields["out_dest"].required=carry_out
                self.data["out_comment"] =''
                self.data["out_date"] =''
                self.data["out_dest"] =''
                
    def clean(self):
        cleaned_data = self.cleaned_data
        carry_in = cleaned_data.get("carry_in")
        carry_out = cleaned_data.get("carry_out")

        if not carry_in and not carry_out:
            raise forms.ValidationError(_(u"攜入或攜出申請至少勾選一個！"))

        emp_no=cleaned_data.get("emp_no")
        try:
            emp = Employee.objects.get(emp_no=emp_no)
            cleaned_data["emp_name"]= emp.name
            cleaned_data["emp_department"] = emp.department.name
            cleaned_data["emp_grade"] = emp.grade
        except Employee.DoesNotExist:
            self._errors["emp_no"] = self.error_class([_(u"找不到此員工信息，請確認輸入無誤。")])
            #raise forms.ValidationError(u"找不到此員工信息，請確認輸入的工號無誤！")
        
        extension = cleaned_data.get('emp_extension')
        telephone = cleaned_data.get('emp_telephone')
        if not telephone and not extension:
            self._errors["emp_extension"] = self.error_class([_(u"联系方式至少填寫一個。")])
        
        _clean_image(cleaned_data)
        
        return cleaned_data
        
    class Meta:
        model = ApplicationCarry
        widgets={
            #"emp_name":BootstrapUneditableInput(),
            #"emp_department":BootstrapUneditableInput(),
            "in_date":BootstrapDateInput(),
            "out_date":BootstrapDateInput(),
        }
        
class ApplicationCardForm(ModelForm):
    """
    管製卡申請單 表單
    """
    applicant_type = forms.ChoiceField(
        label=_(u'申請類型'), 
        choices=(
            ("EMP",_(u"集團員工")),
            ("CUSTOMER",_(u"客戶")),
            ("CUSTOMER-ONSITE",_(u"駐廠客戶")),
        )
    )
    
    def __init__(self,*args,**kwargs):
        super(ApplicationCardForm, self).__init__(*args, **kwargs)
        if args:
            applicant_type = self.fields["applicant_type"].clean(args[0].get("applicant_type"))
            if applicant_type == "EMP":
                self.fields["customer_company"].required = False
                self.fields["customer_name"].required = False
                self.fields["customer_telephone"].required = False
                self.fields["customer_id_type"].required = False
                self.fields["customer_id_no"].required = False
                self.data["customer_company"] =''
                self.data["customer_name"] =''
                self.data["customer_telephone"] =''
                self.data["customer_id_type"] = 0
                self.data["customer_id_no"] = ''
            elif applicant_type.startswith("CUSTOMER"):
                self.fields["emp_no"].required = False
                self.fields["emp_name"].required = False
                self.fields["emp_department"].required = False
                self.fields["emp_grade"].required = False
                self.fields["emp_position"].required = False
                self.fields["emp_extension"].required = False
                self.fields["emp_telephone"].required = False
                self.data["emp_no"] =''
                self.data["emp_name"] =''
                self.data["emp_department"] =''
                self.data["emp_grade"] = ''
                self.data["emp_position"] = ''
                self.data["emp_extension"] = ''
                self.data["emp_telephone"] = ''
                if not applicant_type.startswith("-ONSITE"):
                    self.fields["valid_start_date"].required = True
                    self.fields["valid_end_date"].required = True
                    self.data["valid_start_date"] = ''
                    self.data["valid_end_date"] = ''
                
    class Meta:
        model = ApplicationCard
        widgets={
            "valid_start_date":BootstrapDateInput(),
            "valid_end_date":BootstrapDateInput(),
        }

class DeviceForm_(ModelForm):
    lan_mac = MacField(
        label=_(u"有線網卡MAC地址"),
        required=True,
        help_text=_(u"格式如：AB-CD-EF-12-34-56 <i class='icon-question-sign'></i><a href='#'>如何獲取MAC地址?</a>")
    )
    wifi_mac = MacField(label=_(u"無線網卡MAC地址"),required=False)
    
    class Meta:
        model = ApplicationDevice
    

class TestField(forms.Form):
    from .fields import MacField
    lan_mac = MacField(label=u"Lan MAC Address")
    
class TestForm(ModelForm):
    class Meta:
        model = TestModel
        
class ContactForm(forms.Form):
    subject = forms.CharField(label=u'標題',min_length=5,max_length=20,help_text=u'請輸入標題.')
    message = forms.CharField(label=u'內容',min_length=20)
    sender = forms.EmailField(label=u'發送到')
    cc_myself = forms.BooleanField(label=u'CC給自己',required=False)

class AppTypeForm(forms.Form):
    app_type = forms.TypedChoiceField(label=u'請選擇申請類型', 
                                choices=((APP_TYPE_CARRY_INOUT, u'攜入攜出申請'), 
                                (APP_TYPE_CARD_EMP, u'管製卡(員工)'),
                                (APP_TYPE_CARD_CUSTOMER_ONSITE, u'管製卡(駐廠客戶)'),
                                (APP_TYPE_CARD_CUSTOMER, u'管製卡(客戶)') ),
                                coerce=int,
                                widget=forms.RadioSelect())

class DeviceForm(forms.Form):
    owner = forms.TypedChoiceField(label=u"资产類型",choices=OWNER_CHOICES,required=False,coerce=int,empty_value=OWNER_CHOICES_PERSONAL)
    manufacturer = forms.ChoiceField(label=u'品牌', choices=MANUFACTURER_CHOICES)
    model_no = forms.CharField(label=u"設備型號",max_length=50)
    sn = forms.CharField(label=u"設備序號",max_length=50)
    lan_mac = forms.CharField(label=u"有線網卡MAC地址",max_length=17)
    wifi_mac = forms.CharField(label=u"無線網卡MAC地址",max_length=17,required=True)
    color = forms.ChoiceField(label=u"颜色",choices=COLOR_CHOICES)
    
    def valid_mac_addr(self,value):
        pattern = re.compile(r'^[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}$')
        match = pattern.match(value)
        return match
        
    def clean_lan_mac(self):
        lan_mac=self.cleaned_data['lan_mac']
        match = self.valid_mac_addr(lan_mac)
        if not match:
            self._errors["lan_mac"] = self.error_class([u"MAC地址格式有誤!"])
        return lan_mac.upper()
        
    def clean_wifi_mac(self):
        wifi_mac=self.cleaned_data['wifi_mac']
        match = self.valid_mac_addr(wifi_mac)
        if not match:
            self._errors["wifi_mac"] = self.error_class([u"MAC地址格式有誤!"])
        return wifi_mac.upper()

class CustomerForm(forms.Form):
    customer_name = forms.CharField(label=u"姓名",max_length=50)
    customer_company = forms.CharField(label=u"公司",max_length=50)
    id_type = forms.TypedChoiceField(label=u"證件類型",choices=ID_CHOICES,coerce=int)
    id_no  = forms.CharField(label=u"證件號碼",max_length=30)
    customer_telephone = forms.CharField(label=u"聯繫電話",max_length=20)
    
class EmployeeForm(forms.Form):
    #department_sub1 = forms.ModelChoiceField(label=u"單位",
    #    queryset= Organization.objects.filter(layer=1),
    #    empty_label=u"事業群")
    department = forms.CharField(label=u"單位",
        widget=forms.TextInput(attrs={'readonly':'readonly'})
    )
    emp_name = forms.CharField(label=u"姓名",max_length=50,
        widget=forms.TextInput(attrs={'readonly':'readonly'})
    )
    emp_no = forms.CharField(label=u"工號",max_length=20)
    grade = forms.ChoiceField(label=u"資位",choices=GRADE_CHOICES)
    position = forms.ChoiceField(label=u"管理職",choices=POSTION_CHOICES)
    extension = forms.CharField(label=u"分機號碼",max_length=20,required=False)
    emp_telephone = forms.CharField(label=u"聯繫電話",max_length=20,required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        emp_no=cleaned_data.get("emp_no")
        try:
            emp = Employee.objects.get(emp_no=emp_no)
            cleaned_data["emp_name"]= emp.name
            cleaned_data["department"] = emp.department.name
            extension = cleaned_data['extension']
            telephone = cleaned_data['emp_telephone']
            if not telephone and not extension:
                raise forms.ValidationError(u"联系方式必写一种")
        except Employee.DoesNotExist:
            self._errors["emp_no"] = self.error_class([_(u"找不到此員工!")])
            
        return cleaned_data
    
class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'cols':'50','rows':'3'}))
    
class AttachmentForm(forms.Form):
    id_image = forms.ImageField(label=u"證件影本")
    promise_image = forms.ImageField(label=u"承諾書(含簽名檔)")
    
    def clean(self):
        cleaned_data=self.cleaned_data
        #修改上傳文件的文件名
        import os
        file_ext = os.path.splitext(cleaned_data["id_image"].name)[1]
        file_name = get_uuid_str()
        cleaned_data["id_image"].name = ''.join([file_name,file_ext])
        
        file_ext = os.path.splitext(cleaned_data["promise_image"].name)[1]
        file_name = get_uuid_str()
        cleaned_data["promise_image"].name = ''.join([file_name,file_ext])
        return cleaned_data

class CarryForm(forms.Form):
    applicant_type = forms.TypedChoiceField(label=u'申請類型', choices=CARRY_APPLICANT_TYPE_CHOICES,coerce=int)
    carry_in = forms.BooleanField(label=u'申請攜入',required=False)
    in_date = forms.DateField(label=u"攜入日期",required=False)
    in_dest = forms.CharField(label=u"使用地點",required=False)
    in_comment = forms.CharField(label=u"攜入理由",required=False,widget=forms.Textarea(attrs={'cols':'50','rows':'3'}))
    
    carry_out = forms.BooleanField(label=u'申請攜出',required=False)
    out_date = forms.DateField(label=u"攜出日期",required=False)
    out_dest = forms.CharField(label=u"目的地",required=False)
    out_comment = forms.CharField(label=u"攜出理由",required=False,widget=forms.Textarea(attrs={'cols':'50','rows':'3'}))
    
    def clean(self):
        cleaned_data=self.cleaned_data
        carry_in=cleaned_data.get("carry_in")
        carry_out=cleaned_data.get("carry_out")
        if not carry_in and not carry_out:
            raise forms.ValidationError(u"攜入或者攜出申請必須勾選一個!")
        if carry_in :
            in_date=cleaned_data.get("in_date")
            in_dest=cleaned_data.get("in_dest")
            in_comment=cleaned_data.get("in_comment")
            if not in_date:
                self._errors["in_date"] = self.error_class([u"攜入日期不能為空!"])
            if not in_dest:
                self._errors["in_dest"] = self.error_class([u"使用地点不能為空!"])
            if not in_comment:
                self._errors["in_comment"] = self.error_class([u"携入理由不能為空!"])
        
        if carry_out:
            out_date=cleaned_data.get("out_date")
            out_dest=cleaned_data.get("out_dest")
            out_comment=cleaned_data.get("out_comment")
            if not out_date:
                self._errors["out_date"] = self.error_class([u"攜出日期不能為空!"])
            if not out_dest:
                self._errors["out_dest"] = self.error_class([u"目的地不能為空!"])
            if not out_comment:
                self._errors["out_comment"] = self.error_class([u"携出理由不能為空!"])
        return cleaned_data
        
class CustomerCardForm(forms.Form):
    start_date = forms.DateField(label=u"管製卡有效期")
    end_date = forms.DateField(label=u"至")
    
'''
class TestForm(forms.Form):  
    def __init__(self, query_set=None, *args, **kwargs):  
        super(TestForm, self).__init__(*args, **kwargs)  
        bg = forms.ModelChoiceField(label=u"事業群",  
                                           required=False,  
                                           #widget=CheckboxSelectMultiple,  
                                           queryset=query_set)  
        self.fields['bg'] = bg 
        
class EmpInfoForm(forms.Form):
    bg = forms.ChoiceField()
    bg_1=forms.ChoiceField()
    chu =forms.ChoiceField()
    bu = forms.ChoiceField()
    ke = forms.ChoiceField()
    emp_no =forms.CharField()
    name = forms.CharField()
    sub_phone = forms.CharField()
    grade = forms.CharField()#資位
    position = forms.CharField()#職位
    telephone =forms.CharField()
    
class GuestForm(forms.Form):
    name = forms.CharField(max_length=50)
    company = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20)
    identify_type = forms.CharField(max_length=20)
    identify_no  = forms.CharField(max_length=30)
    emp_no = forms.CharField()
    foxconn_name = forms.CharField()

class AppDetail(forms.Form):
    #app_type = forms.IntegerField(choices=TYPE_CHOICES)# (in,out,card)
    #applicant = forms.ForeignKey(User)
    app_reason = forms.CharField()#textfield
    requested_dt = forms.DateField()#申請攜入.攜出日期
    device_dest = forms.CharField(max_length=50)#申請設備所到地點
'''