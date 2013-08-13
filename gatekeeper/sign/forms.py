from django import forms
from django.forms import ModelForm
from sign.models import *

#class ApplicationForm(ModelForm):
#    app_no = forms.CharFiled()
    
    #class Meta:
    #    model = Application

class DeviceForm(ModelForm):
    class Meta:
        model = Device


        #class User(forms):