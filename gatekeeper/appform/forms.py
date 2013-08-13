from django import forms
from django.forms import ModelForm
from models import *

#class ApplicationForm(ModelForm):
#    app_no = forms.CharFiled()
    
    #class Meta:
    #    model = Application

class DeviceForm(ModelForm):
    class Meta:
        model = Device


#class User(forms):
class AppTypeForm(forms.Form):
    apptype = forms.ChoiceField(label=u'申請類型', 
                                choices=((u'1', u'攜入攜出申請'), 
                                (u'3', u'管製卡(員工)'),
                                (u'4', u'管製卡(駐廠客戶)'),
                                (u'5', u'管製卡(客戶)') ), 
                                widget=forms.RadioSelect())

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

class xxxForm(forms.Form):
    pass