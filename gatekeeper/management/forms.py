#-*-coding:utf-8-*-

#django imports
from django import forms
from django.contrib.auth.models import User,Group

# gk imports
from gatekeeper.account.models import SignedMember,Employee,Organization

class EmpForm(forms.Form):
    emp_no = forms.CharField(label=u"工號",max_length=20)
    
    
class SignerForm(forms.Form):
    emp_no = forms.CharField(label=u"工號",max_length=20)
    group =  forms.ModelChoiceField(label=u"角色",queryset=Group.objects.all(),empty_label=None)

    def clean_emp_no(self):
        """
        驗證EMP_NO是否存在
        """
        try:
            emp_no=self.cleaned_data['emp_no']
            emp=Employee.objects.get(emp_no=emp_no)
        except Employee.DoesNotExist:
            self._errors["emp_no"]=self.error_class([u"找不到此工號"])
        
        return emp_no
        
class MemberModelForm(forms.ModelForm):
    department = forms.CharField(label=u"單位",required=False,
        widget=forms.HiddenInput
    )
    
    class Meta:
        model = Employee
        #fields = ('emp_no', 'name','notes_mail','extension','telephone','grade','position')
        exclude = ('user','department')
    
    #def save(self,*agrs,**kwargs):
    #    print 'save method!'
    #    member = super(MemberModelForm,self).save(*agrs,**kwargs)
    #    member
        
    def clean_emp_no(self):
        emp_no=self.cleaned_data['emp_no']
        employee = Employee.objects.filter(emp_no=emp_no)
        if employee:
            self._errors["emp_no"] = self.error_class([u"此工號已經存在。"])
        return emp_no.upper()
        
    def clean_department(self):
        try:
            org = Organization.objects.get(uuid=self.cleaned_data['department'])
        except Organization.DoesNotExist:
            org = None
        return org
        
    #def clean(self):
        #cleaned_data = self.cleaned_data
        #print cleaned_data
        #emp_no=cleaned_data.get("emp_no")
        #try:
        #    emp = Employee.objects.get(emp_no=emp_no)
        #    cleaned_data["emp_name"]= emp.name
        #    cleaned_data["department"] = emp.department.name
        #    extension = cleaned_data['extension']
        #    telephone = cleaned_data['emp_telephone']
        #    if not telephone and not extension:
        #        raise forms.ValidationError(u"联系方式必写一种")
        #except Employee.DoesNotExist:
        #    pass
            #raise forms.ValidationError(u"找不到此員工!")
            
        #return cleaned_data