#-*-coding:utf-8 -*-

#django imports
from django import forms
from django.utils.translation import ugettext_lazy as _

class PersonInformationForm(forms.Form):
    old_password = forms.CharField(label=_(u"舊密碼"), widget=forms.PasswordInput)
    notes_mail = forms.CharField(label=_(u"Notes郵箱"), max_length=100)
    extension = forms.CharField(label=u"分機號碼",max_length=20)
    telephone = forms.CharField(label=u"聯繫電話",max_length=20,required=False)
    
    def __init__(self,user,*args,**kwargs):
        self.user = user
        super(PersonInformationForm,self).__init__(*args,**kwargs)
        
    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_(u"你的舊密碼不正確。請重新輸入。"))
        return old_password