# -*- coding: utf-8 -*-

#django imports
from django.db import models
from django.contrib.auth.models import User,Group
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

#gatekeeper imports
from gatekeeper.account.settings import GRADE_CHOICES,POSTION_CHOICES


class Organization(models.Model):
    """
    組織架構表
    """
    uuid = models.CharField(max_length=50,primary_key=True)
    name = models.CharField(max_length=256)
    parent = models.ForeignKey('self',null=True)
    #layer = models.IntegerField()
    class Meta:
        db_table = u'c_organization'
    def __unicode__(self):
        return u'%s' %(self.name)


class SignedMember(models.Model):
    employee = models.ForeignKey("Employee",related_name='signer')
    department = models.ForeignKey(Organization)
    group = models.ForeignKey(Group)
    agent = models.ForeignKey("Employee",null=True,related_name='agent')
    agent_enabled = models.BooleanField(default=False)
    
    class Meta:
        db_table = u'c_signed_member'
        
        
class Department(models.Model):
    """
    部門表
    由組織架構表生成的詳細部門表
    """
    name = models.CharField(max_length=255)
    has_layers = models.IntegerField(null=True)
    class Meta:
        db_table = u'c_department'
    def __unicode__(self):
        return u'%s' %(self.name)

class Employee(models.Model):
    """
    員工信息表
    """
    emp_no = models.CharField(_(u"工號"),max_length=50,primary_key=True)
    user = models.OneToOneField(User,null=True,verbose_name=_(u"用户名"))
    name = models.CharField(_(u"姓名"),max_length=50,null=True)
    notes_mail = models.CharField(_(u"邮箱"),max_length=100,null=True,blank=False)
    extension = models.CharField(_(u"分機號"),max_length=50,null=True,blank=True)
    telephone = models.CharField(_(u"手機"),max_length=50,null=True,blank=True)
    grade = models.CharField(_(u"資位"),max_length=50,choices=GRADE_CHOICES,null=True,blank=True)
    position = models.CharField(_(u"管理職"),max_length=50,choices=POSTION_CHOICES,null=True,blank=True)
    department = models.ForeignKey(Organization,null=True,verbose_name=_(u"部門"))  #此字段有修改
    
    class Meta:
        db_table = u'c_employee'
   
    def __unicode__(self):
        return u'%s' %(self.name)
        
'''
class EmpGrade(models.Model):
    """
    員工資位表
    """
    name = models.CharField(max_length=20)
    level = models.IntegerField(unique=True)
    class Meta:
        db_table = u'c_emp_grade'
   
    def __unicode__(self):
        return u'%s' %(self.name)
        
class EmpPostion(models.Model):
    """
    員工管理職表
    """
    name = models.CharField(max_length=20)
    level = models.IntegerField(unique=True)
    class Meta:
        db_table = u'c_emp_postion'
   
    def __unicode__(self):
        return u'%s' %(self.name)

class Permission(models.Model):
    """
    與Role綁定的權限表
    """
    name = models.CharField(_('name'), max_length=50)
    codename = models.CharField(_('codename'), max_length=100)
    #content_type = models.ForeignKey(ContentType)
    #objects = PermissionManager()
    
    class Meta:
        db_table = u'c_permission'
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        #unique_together = (('content_type', 'codename'),)
        #ordering = ('content_type__app_label', 'content_type__model', 'codename')

    def __unicode__(self):
        return u"%s" % (
            #unicode(self.content_type.app_label),
            #unicode(self.content_type),
            unicode(self.name))

class Role(models.Model):
    """
    角色Role表
    """
    name = models.CharField(max_length=50)
    user = models.ManyToManyField(User)
    role_permission = models.ManyToManyField(Permission,blank=True)
    
    class Meta:
        db_table = u'c_role'
   
    def __unicode__(self):
        return u'%s' %(self.name)
                
'''