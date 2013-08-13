# -*- coding: utf-8 -*-

#python imports
import time 
import uuid
import hashlib

#django imports
from django.db import models
from django.contrib.auth.models import User,Group
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
#from django.utils.hashcompat import md5_constructor, sha_constructor

#gatekeeper imports
from gatekeeper.account.models import Employee,Department,SignedMember,Organization
from gatekeeper.account.settings import GRADE_CHOICES,POSTION_CHOICES
from .settings import ROUTE_ACTION_CHOICES
from .settings import ROUTE_ACTION_SUBMIT,ROUTE_ACTION_AGREE,ROUTE_ACTION_REJECT,ROUTE_ACTION_DONE

from .settings import APP_STATUS_NAME_CHOICES,APP_STATUS_DISPLAYNAME_CHOICES
from .settings import APP_STATUS_SINGER_LABEL_CHOICES,APP_STATUS_TIME_LABEL_CHOICES
from .settings import APP_TYPE_CHOICES
from .settings import OWNER_CHOICES,MANUFACTURER_CHOICES,COLOR_CHOICES,ID_CHOICES
from .settings import APP_STATUS_SUBMIT
from .settings import APP_STATUS_MAKE_CARD
from .settings import APP_STATUS_IN_GUARD_CHECK
from .settings import APP_STATUS_OUT_GUARD_CHECK
from .settings import APP_STATUS_REJECTED
from .settings import APP_STATUS_HR_APPROVE

from .settings import APP_TYPE_CARRY_INOUT
from .settings import APP_TYPE_CARRY_IN
from .settings import APP_TYPE_CARRY_OUT
from .settings import APP_TYPE_CARD_EMP
from .settings import APP_TYPE_CARD_CUSTOMER
from .settings import APP_TYPE_CARD_CUSTOMER_ONSITE
from .settings import APP_TYPE_ROUTE_NAME

#NOW = time.localtime()
#DATENOW = time.strftime('%Y-%m-%d',NOW)
#TIMENOW = time.strftime('%H:%M:%S',NOW)
#DATETIMENOW = time.strftime('%Y-%m-%d %H:%M:%S',NOW)

class TestForeign(models.Model):
    bg = models.ForeignKey("TestModel",null=True,on_delete=models.SET_NULL)
    
class TestModel(models.Model):
    bg = models.CharField(max_length=50)
    slug = models.SlugField()
    
    def save(self, *args, **kwargs):
        #self.bg = "cesbg"
        super(TestModel, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return u'%s'% self.bg
        
'''
class Test(models.Model):
    image = models.FileField(u'文件',upload_to='images/%Y-%m/')
'''

def get_department_tree(department):
    """
    返回 department 所對應到root的所有部門node
    """
    department_list = []
    #try:
    #    node = Organization.objects.get(uuid = uuid)
    #except Organization.DoesNotExist:
    #    node = None
    if isinstance(department,Organization):
        node = department    
    else:
        return False
        
    while node :
        department_list.append(node)
        try:
            node = node.parent
        except Organization.DoesNotExist:
            node = None
            
    return department_list
    
def get_appid_crc(app_id):
    """
    產生混淆字串
    """
    return hashlib.md5(app_id+'gatekeeper-tao').hexdigest().upper()[0:4]
    
def generate_appid(prefix):
    """
    生成申請單號
    prefix: "CARRY"(攜入攜出),"CARD"(管製卡)
    """
    if not prefix:
        return None
    now_time = time.localtime()
    date_str = time.strftime('%y%m%d',now_time)
    appid_prefix = ''.join(['TJ',prefix.upper(),date_str])
    
    try:
        last_number = ApplicationBase.objects.filter(number__startswith=appid_prefix).order_by('-number')[0].number
        app_id = ''.join([appid_prefix , str(int(last_number[-8:-4])+1).zfill(4)])
    except ApplicationBase.DoesNotExist:
        app_id = appid_prefix + '0001'
    except IndexError:
        app_id = appid_prefix + '0001'
    
    app_id =''.join([app_id,get_appid_crc(app_id)])
    return app_id

def do_signed(curr_user,app,action,comment=u''):
    """
    
    """
    if action == 'agree':
        comment = u''
    elif action != 'reject':
        return False
    elif action == 'reject' and comment == u'':
        return False
    
    r_m = RouteManager(app)
    curr_station = r_m.get_curr_station(app_status=app.status,action=action)
    
    if curr_station:
        need_role = curr_station.role #取得當前簽核需要的role
        #TODO:結合部門來選擇簽核人是否正確。
        signer = User.objects.get(role=need_role)
        if curr_user == signer:
            #添加簽核歷史
            sh=SignedHistory.objects.add(app=app,role=need_role,signed_by=curr_user.first_name,
                                      app_status=app.status,comment=comment,condition=action)
            if sh:
                r_m.set_app_next_station(action=action)
                return True
    
def create_application(app_type,class_type,request):
    data_dict={}
    keylist = request.POST.keys()
    for key in keylist:
        data_dict[key] = request.POST[key]
    # 處理上傳的附件
    data_dict['id_image'] = request.FILES.get('id_image',None)

    data_dict['promise_image'] = request.FILES.get('promise_image',None)
    
    app = Application.objects.create_app(app_type=app_type,class_type=class_type,
                                         submit_user= request.user,data=data_dict)
    route_manager = RouteManager(app)
    route_manager.handle_submit_app()
    return app
    
class RouteManager(object):
    """
    簽核路由管理類
    """
    def __init__(self,app):
        self.app = app
        #print app
        if  self.app.app_type=='card':
            self.app_card = ApplicationCard.objects.get(application=app)
        
    def get_unsigner_list(self):
        """
        得到申請單待簽核人員列表
        """
        unsigner_list= []
        print self.app.status
        
        curr_station = self.get_curr_station(app_status=self.app.status,action='agree')#從app的status開始
        while True:
            if curr_station :
                signer_name = self.get_unsigner_name(curr_station.role)
                if signer_name :
                    unsigner_list.append({'signer_name':signer_name,'role_name':curr_station.role.name})
                    print {'signer_name':signer_name,'role_name':curr_station.role.name}
                else:
                    unsigner_list.append({'signer_name':u'NotFoundSigner','role_name':curr_station.role.name})
                
                next_station = self.get_next_station(app_status=curr_station.app_status,action='agree')
                if next_station :
                    curr_station = next_station
                    #app_status = next_station.app_status
                else:
                    break
            else:
                break
        
        return unsigner_list

    def get_unsigner_name(self,role,real_user=None):
        try:
            signer = User.objects.get(role=role)#TODO:添加部門的過濾，這裡僅作測試使用!!!
            return signer.first_name
        except Exception,e:
            print u'NotFoundSigner'
            print e        
    
    def handle_submit_app(self):
        route_header = RouteHeader.objects.get(route_name=self.app.route_name)
        #判斷簽核歷史是否為空
        #try:
        #    signed_history = SignedHistory.objects.fillter(application=self.app)
        #except:
        #    signed_history = None
        app_status = self.app.status
        if app_status.name == 'submit':
            role = Role.objects.get(name='user')
            signed_history = SignedHistory.objects.add(app=self.app,
                                            signed_by=self.app.submit_by.first_name,
                                            app_status=app_status,role = role)
            signed_history.save()
            self.set_app_next_station(action='submit')

    def set_app_next_station(self,action):
        next_station = self.get_next_station(app_status=self.app.status,action=action)
        if next_station:
            self.app.status = next_station.app_status
            self.app.save()
            return next_station
    
    def get_curr_station(self,app_status,action):        
        try:
            curr_station = SignatureRoute.objects.get(route_name=self.app.route_name,
                                          action=action,app_status = app_status)
            
            return curr_station
        except Exception,e:
            print u'NotFoundCurrStation'
            print e
        
    def get_next_station(self,app_status,action):
        try:
            #curr_station = SignatureRoute.objects.get(route_name=self.app.route_name,
            #                                          action=action,app_status = self.app.status)
            curr_station = self.get_curr_station(app_status = app_status,action=action)
            next_station = curr_station.next_route
            return next_station
        except Exception,e:
            print u'NotFoundNextStation'
            print e

class ApplicationManager(models.Manager):
    def create_app(self,app_type,class_type,submit_user,data):
        """
        創建申請單
        """
        app_id = generate_appid()
        import os
        file_type = os.path.splitext(data['id_image'].name)[1]
        data['id_image'].name = ''.join([app_id,'_id',file_type])
        file_type = os.path.splitext(data['promise_image'].name)[1]
        data['promise_image'].name = ''.join([app_id,'_promise',file_type])
        
        app_status = AppStatus.objects.get(name='submit')
        route_name = class_type
        
        app = self.model(app_id=app_id,app_type=app_type,class_type=class_type,
                         status=app_status,route_name=route_name,submit_by=submit_user)
        app.save(using=self._db)
        if app_type =='card':
            app_card = self.create_app_card(app,data)
        elif app_type =='carry':
            pass
        return app
        
    def create_app_card(self,app,data):
        start_date = data.get('start_date',None)
        end_date = data.get('end_date',None)
        owner = data.get('owner','')
        wifi_mac = data.get('wifi_mac','')
        emp_no = data.get('emp_no','')
        company = data.get('company','')
        grade = data.get('grade','')

        position = data.get('position','')
        extension = data.get('extension','')
        telephone = data.get('telephone','')
        id_type = data.get('id_type','')
        id_no = data.get('id_no','')
        app_card = ApplicationCard(application=app,comment=data['comment'],
            start_date=start_date,end_date=end_date,
            owner=owner,manufacturer=data['manufacturer'],
            model_no=data['model_no'],color=data['color'],
            sn=data['sn'],lan_mac=data['lan_mac'],wifi_mac=wifi_mac,
            emp_no = emp_no,name=data['name'],
            company=company,grade=grade,
            position=position,extension=extension,
            telephone=telephone,
            id_type=id_type,id_no=id_no,
            id_image = data['id_image'],promise_image=data['promise_image']
            )
        app_card.save(force_insert=True)
        return app_card
        
    def create_app_in_out(self,app,data):
        pass

class SignedHistoryManager(models.Manager):
    def get_history(self,app):
        sh = self.filter(application=app).order_by('id') \
                    .extra(select={'role_name':'c_role.name'},tables=['c_role'],\
                           where=['r_signed_history.role_id=c_role.id']) \
                    .values('date','signed_by','comment','condition','app_status','role_name')
        #print list(sh)
        #print siged_history
        #history = []
        #for history_row in sh:
        #    history.append(history_row)
        #print history\
        return sh
        
    def add(self,app,role,app_status,signed_by,comment=u'',condition=u''):
        try:
            #role = Role.objects.get(name=role_name)
            #app_status = AppStatus.objects.get(status='submit')
            signed_history = SignedHistory(application=app,signed_by=signed_by,
                                        app_status=app_status.name,role=role,
                                        comment=comment,condition=condition)
            signed_history.save()
            return signed_history
        except Exception,e:
            print u'FailedAddHistory'
            print e

def get_uuid_str():
    return str(uuid.uuid4())
    
class RouteHeader(models.Model):
    """
    簽核路由 指針表
    功能:指向對應路由的首站(station)
    """
    route_name = models.CharField(u"路由名",max_length=50,unique=True)
    header = models.ForeignKey("SignatureRoute",null=True,blank=True,verbose_name=u"頭部指針")
    
    def __unicode__(self):
        return u'%s'% self.route_name
        
    class Meta:
        db_table = u'c_route_header'

class SignatureRoute(models.Model):
    """
    簽核路由表
    """
    route_name = models.ForeignKey(RouteHeader,null=True,blank=True)
    group = models.ForeignKey(Group,null=True,blank=True)
    action = models.PositiveSmallIntegerField(choices=ROUTE_ACTION_CHOICES,null=True,blank=True)
    app_status = models.ForeignKey("ApplicationStatus")
    next_route = models.ForeignKey("self",null=True,blank=True)
    
    def __unicode__(self):
        if self.next_route:
            return u'[id:%s] name:%s|group:%s|action:%s|app_status:%s|next_status:%s'% (self.id,self.route_name,self.group,self.get_action_display(),self.app_status,self.next_route.app_status)
        else:
            return u'[id:%s] name:%s|group:%s|action:%s|app_status:%s|next_status:NULL'% (self.id,self.route_name,self.group,self.get_action_display(),self.app_status)
    class Meta:
        db_table = u'c_signature_route'
        


class ApplicationAuth(models.Model):
    """
    資安設備授權用戶
    """
    bg_bu = models.ForeignKey(Department)
    authorizer = models.ForeignKey(User,related_name="authorizer")
    agent = models.ForeignKey(User,related_name="agent")
    enabled_agent = models.BooleanField()
    group = models.ForeignKey(Group)
    
    class Meta:
        db_table = u'c_application_auth'

class ApplicationStatus(models.Model):
    """
    申請單狀態表
    """
    name = models.PositiveSmallIntegerField(choices=APP_STATUS_NAME_CHOICES,unique=True)
    display_name = models.PositiveSmallIntegerField(choices=APP_STATUS_DISPLAYNAME_CHOICES,null=True,blank=True)
    signer_label = models.PositiveSmallIntegerField(choices=APP_STATUS_SINGER_LABEL_CHOICES,null=True,blank=True)
    time_label = models.PositiveSmallIntegerField(choices=APP_STATUS_TIME_LABEL_CHOICES,null=True,blank=True)
    
    def __unicode__(self):
        return u'%s-%s'% (self.id,self.get_name_display())
        
    class Meta:
        db_table = u'c_application_status'
        verbose_name = u"Application Status"
        verbose_name_plural = u"Application Statuses"
        
def get_submit_status():
    #submit_status = ApplicationStatus.objects.get(name=APP_STATUS_SUBMIT)
    return ApplicationStatus.objects.get(name=APP_STATUS_SUBMIT)

def get_app_status_object(name):
    """
    建立一個 申請單狀態 模型
    成功返回:ApplicationStatus Object
    失敗返回:None
    """
    #submit_status = ApplicationStatus.objects.get(name=APP_STATUS_SUBMIT)
    try:
        return ApplicationStatus.objects.get(name=name)
    except Exception:
        return None
        
def _get_route(type_code):
    """
    返回路由
    """
    for type,route_name,app_name in APP_TYPE_ROUTE_NAME:
        if type == type_code:
            route = RouteHeader.objects.get(route_name=route_name)
            return route
            
class ApplicationBase(models.Model):
    """
    申請單 基礎模型
    """
    number = models.CharField(max_length=255,unique=True)
    type_code = models.CharField(max_length=255)
    status = models.ForeignKey(ApplicationStatus,default=get_submit_status)
    route = models.ForeignKey(RouteHeader,null=True)
    submit = models.ForeignKey(User,related_name='submit')
    created_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    uid = models.CharField(max_length=50,default=get_uuid_str)
    
    def save(self,*args,**kwargs):
        self.route = _get_route(self.type_code)
        super(ApplicationBase,self).save(*args,**kwargs)
    
    def _get_app_name(self):
        for type,route_name,app_name in APP_TYPE_ROUTE_NAME:
            if type == self.type_code:
                return app_name
    app_name = property(_get_app_name)
    
    def has_signed_perm(self,user):
        signer_list = self.get_current_signer()
        if user.employee in signer_list:
            return True
        else:
            return False
        
    def do_signed(self,user,action,comment=u''):
        """
        簽核動作...
        action : ROUTE_ACTION
        """
        if self.has_signed_perm(user=user) :
            special_status = [APP_STATUS_MAKE_CARD,APP_STATUS_IN_GUARD_CHECK]
            if self.status.name in special_status:
                action = ROUTE_ACTION_DONE
            if action == ROUTE_ACTION_REJECT and not comment:
                return False
            elif action == ROUTE_ACTION_AGREE and comment:
                comment = ''
            app_history = ApplicationHistory.objects.create(
                application = self,
                signer = user,
                action = action,
                comment = comment,
                app_status = self.status,
                uid = self.uid,
            )
                
            self.set_app_next_station(action=action)
            return True
        else:
            return False
        
    def get_current_signer(self):
        """
        返回當前簽核人列表
        格式: [Employee Object,...]
        """
        signer_list = []
        curr_station = self.get_curr_station(app_status=self.status,action = ROUTE_ACTION_AGREE)
        if curr_station is None:
            curr_station = self.get_curr_station(app_status=self.status,action = ROUTE_ACTION_DONE)
        
        if curr_station is not None:
            signer_list = self.get_unsigner(curr_station.group)
            #signer_list.append(signer)
        
        return signer_list
        
    def get_unsigner_list(self):
        """ 
        得到申請單待簽核人員列表
        返回格式:[{'status':ApplicationStatus Object,'signer':Employee Object},...]
        """
        unsigner_list= []
        
        # 搜索對應簽核路由的每一個Station
        app_status = self.status
        while True:
            # 路由終止
            if app_status.name in [
                APP_STATUS_IN_GUARD_CHECK,APP_STATUS_OUT_GUARD_CHECK,
                APP_STATUS_REJECTED,APP_STATUS_MAKE_CARD]:
                break
            
            # 處理管製卡中,員工管理職不夠,顯示'副總簽核'欄位邏輯
            if app_status.name == APP_STATUS_HR_APPROVE and \
               self.submit.employee.position not in [u"協理",u"資深協理",u"副總",u"資深副總",u"總裁"]:
                action = ROUTE_ACTION_REJECT
            else:
                action = ROUTE_ACTION_AGREE
                
            curr_station = self.get_curr_station(app_status=app_status,action = action)
            
            if curr_station :
                signer_list = self.get_unsigner(curr_station.group)
                if signer_list:
                    signer = signer_list[0]
                else:
                    signer = None
                unsigner_list.append({'status':curr_station.app_status,'signer':signer})
                # 指向下一個狀態
                app_status = curr_station.next_route.app_status
            else:
                break
            
        return unsigner_list

    def get_unsigner(self,group):
        """
        成功返回簽核人(Employee Object)列表,
        失敗返回 [].
        """
        if not hasattr(self,'signer_department'):
            self.signer_department = self.get_signer_department()
            self.signer_department_tree = get_department_tree(department=self.signer_department)
            #print self.signer_department_tree
        
        try:
            signer_list = []
            #print department_all
            for node in self.signer_department_tree:
                # 一個角色(group)可以對應多個簽核人
                # 目前顯示的待簽核列表以filter第一個
                # TODO:代理人設置及優先級設定? 
                signer_query = SignedMember.objects.filter(department=node,group=group)
                if signer_query :
                    signer_list = [signer.employee for signer in signer_query]
                    #如果找到簽核人,就不再往上層查找
                    break
            
            '''
            cesbg = Organization.objects.get(name='CESBG')
            department = self.submit.employee.department
            if group.name =='HR APPROVE':
                signer = SignedMember.objects.get(department=cesbg,group=group)
            elif group.name =='SPECIAL APPROVE':
                signer = SignedMember.objects.get(department=cesbg,group=group)
            elif group.name =='IT CHECK':
                signer = SignedMember.objects.get(department=cesbg,group=group)
            elif group.name =='IT APPROVE':
                signer = SignedMember.objects.get(department=cesbg,group=group)
            elif group.name =='Department Check':
                signer = SignedMember.objects.get(department=department,group=group)
            else:
            
                signer = SignedMember.objects.get(department=department,group=group)
            # TODO:增加其他狀態的簽核信息
            '''
            
        except Employee.DoesNotExist:
            pass

        return signer_list
        
    def get_app_detail_cls(self):
        type_code = self.type_code
        if type_code.startswith('CARRY') :
            cls_app = ApplicationCarry.objects.get(application = self)
        
        return cls_app
    
    def get_carry_object(self):
        """返回 攜入攜出申請單 Object
        """
        carry_object={}
        try:
            if self.type == APP_TYPE_CARRY_INOUT:
                carry_in = ApplicationIn.objects.get(application=self)
                carry_out = ApplicationOut.objects.get(application=self)
                carry_object["in"]=carry_in
                carry_object["out"]=carry_out
            elif self.type == APP_TYPE_CARRY_IN:
                carry_in = ApplicationIn.objects.get(application=self)
                carry_object["in"]=carry_in
            elif self.type == APP_TYPE_CARRY_OUT :
                carry_out = ApplicationOut.objects.get(application=self)
                carry_object["out"]=carry_out
        except Exception,e:
            print e
            
        return carry_object
        
    def get_signer_department(self):
        """
        返回簽核人的部門
        """
        try:
            department = None
            type_code = self.type_code
            if type_code.startswith('CARRY') :
                department = self.submit.employee.department
            '''
            if self.type == APP_TYPE_CARD_EMP:
                app = ApplicationCard.objects.get(application=self)
                emp = Employee.objects.get(emp_no=app.emp_no)
                department = emp.department
                
            elif self.type in [APP_TYPE_CARD_CUSTOMER,APP_TYPE_CARD_CUSTOMER_ONSITE]:
                department = self.submit.employee.department
            elif self.type in [APP_TYPE_CARRY_INOUT,APP_TYPE_CARRY_IN,APP_TYPE_CARRY_OUT]:
                if self.type==APP_TYPE_CARRY_OUT:
                    app = ApplicationOut.objects.get(application=self)
                else:
                    app = ApplicationIn.objects.get(application=self)

                emp = Employee.objects.get(emp_no=app.emp_no)
                department = emp.department
            '''
        finally:
            pass
            
        return department
        
    def get_user_name(self):
        """
        返回 使用人/攜帶人 姓名
        """
        try:
            name = ''
            
            type_code = self.type_code
            if type_code.startswith("CARRY"):
                app = ApplicationCarry.objects.get(application=self)
                if type_code.endswith("EMP"):
                    name = app.emp_name
                elif type_code.endswith("CUSTOMER"):
                    name = app.customer_name
                    
            '''
            if self.type == APP_TYPE_CARD_EMP:
                app = ApplicationCard.objects.get(application=self)
                name = app.emp_name
            elif self.type in [APP_TYPE_CARD_CUSTOMER,APP_TYPE_CARD_CUSTOMER_ONSITE]:
                app = ApplicationCard.objects.get(application=self)
                name = app.customer_name
            elif self.type in [APP_TYPE_CARRY_INOUT,APP_TYPE_CARRY_IN,APP_TYPE_CARRY_OUT]:
                if self.type==APP_TYPE_CARRY_OUT:
                    app = ApplicationOut.objects.get(application=self)
                else:
                    app = ApplicationIn.objects.get(application=self)
                    
                if app.customer_name:
                    name = app.customer_name
                else:
                    name = app.emp_name
            '''
        finally:
            pass
            
        return name
         
    def _get_submit_email(self):
        """
        返回申請提交人的郵箱地址
        """
        try:
            return self.submit.employee.notes_mail
        except Exception:
            return None
    submit_email = property(_get_submit_email)
    
    def handle_submit_status(self):
        """處理申請單提交狀態
        """
        try:
            if self.status.name == APP_STATUS_SUBMIT:
                app_history = ApplicationHistory.objects.create(
                    application = self,
                    signer = self.submit,
                    action = ROUTE_ACTION_SUBMIT,
                    app_status = self.status,
                    uid = self.uid,
                )
                self.set_app_next_station(action=ROUTE_ACTION_SUBMIT)
            return True
        except Exception,e:
            print Exception,e
            return False

    def set_app_next_station(self,action=None):
        """設置app status為下一個station
        """
        next_station = self.get_next_station(action=action,app_status=self.status)
        if next_station:
            self.status = next_station.app_status
            self.save()
            return next_station
        else:
            return None
        
    def get_curr_station(self,action=None,app_status=None):
        """返回當前station
        """
        try:
            curr_station = SignatureRoute.objects.get(
                route_name=self.route,
                action=action,
                app_status = app_status
            )
            return curr_station
        except (SignatureRoute.MultipleObjectsReturned ,SignatureRoute.DoesNotExist):
            return None
            
    def get_next_station(self,action=None,app_status=None):
        """返回下一個Station
        """
        try:
            curr_station = self.get_curr_station(app_status = app_status,action=action)
            next_station = curr_station.next_route
            return next_station
        except SignatureRoute.DoesNotExist:
            return None
        
    def __unicode__(self):
        return u'%s'% self.number
        
    class Meta:
        db_table = u'r_application_base'
        permissions =(
            ('view_all_status',u'能查看所有申請單信息'),
            ('view_guard_status',u'能查看門崗狀態申請單'),
        )
        
class ApplicationCard(models.Model):
    """
    管製卡申請單 模型
    """
    application = models.ForeignKey(ApplicationBase,unique=True,editable=False)
    comment = models.TextField(_(u"申請理由"))
    valid_start_date =models.DateField(_(u"有效期開始"),null=True,blank=False)
    valid_end_date = models.DateField(_(u"有效期結束"),null=True,blank=False)
    
    #設備信息
    device = models.ForeignKey("ApplicationDevice",editable=False)
    
    #攜帶人/接待人信息
    emp_no = models.CharField(_(u"工號"),max_length=20)
    emp_name = models.CharField(_(u"姓名"),max_length=50)
    emp_department = models.CharField(_(u"單位"),max_length=255)
    emp_grade = models.CharField(_(u"資位"),max_length=50,choices=GRADE_CHOICES,blank=True)
    emp_position = models.CharField(_(u"管理職"),max_length=50,choices=POSTION_CHOICES)
    emp_extension = models.CharField(_(u"分機號碼"),max_length=20,blank=True)
    emp_telephone = models.CharField(_(u"聯繫電話"),max_length=20,blank=True)
    
    #來訪人信息
    customer_company = models.CharField(_(u"公司"),max_length=50,)
    customer_name = models.CharField(_(u"姓名"),max_length=50,)
    customer_telephone = models.CharField(_(u"聯繫電話"),max_length=20,)
    customer_id_type = models.PositiveSmallIntegerField(_(u"證件類型"),choices=ID_CHOICES,default=0)
    customer_id_no  = models.CharField(_(u"證件號碼"),max_length=30)
    
    id_image = models.ImageField(_(u'證件影印'),upload_to='images/attachment/%Y-%m/')
    promise_image = models.ImageField(_(u'承諾書（含簽名檔）'),upload_to='images/attachment/%Y-%m/')
    
    modify_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return u'%s'% self.application.number
        
    class Meta:
        db_table = u'r_application_card'
    
class ApplicationCarry(models.Model):
    """
    攜入攜出申請單 模型
    """
    application = models.ForeignKey(ApplicationBase, unique=True,editable=False)
    #設備信息
    device = models.ForeignKey("ApplicationDevice",editable=False)
    
    #攜入部份
    in_comment = models.TextField(_(u"攜入理由"))
    in_date = models.DateField(_(u"攜入日期"),null=True)
    in_dest = models.CharField(_(u"使用地點"),max_length=50)
    
    #攜出信息
    out_comment = models.TextField(_(u"攜出理由"))
    out_date = models.DateField(_(u"攜出日期"),null=True)
    out_dest = models.CharField(_(u"目的地"),max_length=50)
    
    #攜帶人/接待人信息
    emp_no = models.CharField(_(u"工號"),max_length=20)
    emp_name = models.CharField(_(u"姓名"),max_length=50)
    emp_department = models.CharField(_(u"單位"),max_length=255)
    emp_grade = models.CharField(_(u"資位"),max_length=50,choices=GRADE_CHOICES,blank=True)
    emp_position = models.CharField(_(u"管理職"),max_length=50,choices=POSTION_CHOICES)
    emp_extension = models.CharField(_(u"分機號碼"),max_length=20,blank=True)
    emp_telephone = models.CharField(_(u"聯繫電話"),max_length=20,blank=True,help_text=_(u"集團短號或手機號，如：566+42654321"))
    
    #來訪人信息
    customer_company = models.CharField(_(u"公司"),max_length=50,)
    customer_name = models.CharField(_(u"姓名"),max_length=50,)
    customer_telephone = models.CharField(_(u"聯繫電話"),max_length=20)
    customer_id_type = models.PositiveSmallIntegerField(_(u"證件類型"),choices=ID_CHOICES,default=0)
    customer_id_no  = models.CharField(_(u"證件號碼"),max_length=30)
    
    id_image = models.ImageField(_(u'證件影印'),upload_to='images/attachment/%Y-%m/')
    #promise_image = models.ImageField(_(u'承諾書（含簽名檔）'),upload_to='images/attachment/%Y-%m/')
    
    modify_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
        
    def __unicode__(self):
        return u'%s'% self.application.number
        
    class Meta:
        db_table = u'r_application_carry'
        
class ApplicationIn(models.Model):
    """
    攜入申請單 模型
    """
    application = models.ForeignKey(ApplicationBase, unique=True)
    #攜入部份
    union_out = models.BooleanField(default=False)
    in_comment = models.TextField()
    in_date = models.DateField()
    in_dest = models.CharField(max_length=50)

    #設備信息
    device = models.ForeignKey("ApplicationDevice")
    
    #攜帶人/接待人信息
    emp_no = models.CharField(max_length=20,default='')
    emp_name = models.CharField(max_length=50,default='')
    department = models.CharField(max_length=255,default='')
    grade = models.CharField(max_length=50,choices=GRADE_CHOICES,null=True)
    position = models.CharField(max_length=50,choices=POSTION_CHOICES,null=True)
    extension = models.CharField(max_length=20,default='')
    emp_telephone = models.CharField(max_length=20,default='')
    
    #來訪人信息
    customer_company = models.CharField(max_length=50,default='')
    customer_name = models.CharField(max_length=50,default='')
    customer_telephone = models.CharField(max_length=20,default='')
    id_type = models.PositiveSmallIntegerField(choices=ID_CHOICES,null=True)
    id_no  = models.CharField(max_length=30,default='')
    
    id_image = models.ImageField(u'證件影印',upload_to='images/attchment/%Y-%m/')
    promise_image = models.ImageField(u'承諾書（含簽名檔）',upload_to='images/attchment/%Y-%m/')
    
    modify_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s'% self.application.number
    class Meta:
        db_table = u'r_application_in'
        
class ApplicationOut(models.Model):
    """
    攜出申請單 模型
    """
    application = models.ForeignKey(ApplicationBase, unique=True)
    #攜出信息
    out_date = models.DateField()
    out_dest = models.CharField(max_length=50)
    out_comment = models.TextField()

    #設備信息
    device = models.ForeignKey("ApplicationDevice")
    
    #攜帶人/接待人信息
    emp_no = models.CharField(max_length=20,default='')
    emp_name = models.CharField(max_length=50,default='')
    department = models.CharField(max_length=255,default='')
    grade = models.CharField(max_length=50,choices=GRADE_CHOICES,null=True)
    position = models.CharField(max_length=50,choices=POSTION_CHOICES,null=True)
    extension = models.CharField(max_length=20,default='')
    emp_telephone = models.CharField(max_length=20,default='')
    
    #來訪人信息
    customer_company = models.CharField(max_length=50,default='')
    customer_name = models.CharField(max_length=50,default='')
    customer_telephone = models.CharField(max_length=20,default='')
    id_type = models.PositiveSmallIntegerField(choices=ID_CHOICES,null=True)
    id_no  = models.CharField(max_length=30,default='')
    
    id_image = models.ImageField(u'證件影印',upload_to='images/attchment/%Y-%m/')
    promise_image = models.ImageField(u'承諾書（含簽名檔）',upload_to='images/attchment/%Y-%m/')
    
    modify_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'%s'% self.application.number
    class Meta:
        db_table = u'r_application_out'
        
class ApplicationDevice(models.Model):
    """
    設備信息
    """
    owner = models.PositiveSmallIntegerField(_(u"资产類型"),choices=OWNER_CHOICES)
    manufacturer = models.PositiveSmallIntegerField(_(u"品牌"),choices=MANUFACTURER_CHOICES)
    model_no = models.CharField(_(u"型號"),max_length=50)
    color = models.PositiveSmallIntegerField(_(u"颜色"),choices=COLOR_CHOICES)
    sn = models.CharField(_(u"設備序號"),max_length=50)
    lan_mac = models.CharField(_(u"有線網卡MAC地址"),max_length=17)
    wifi_mac = models.CharField(_(u"無線網卡MAC地址"),max_length=17)
    
    def __unicode__(self):
        return u'SN:%s'% self.sn
    class Meta:
        db_table = u'r_application_device'
        
class ApplicationHistory(models.Model):
    """
    申請單歷史記錄表
    """
    application =  models.ForeignKey("ApplicationBase")
    date  = models.DateTimeField(auto_now_add=True)
    signer = models.ForeignKey(User)
    comment = models.CharField(max_length=100,default='')
    action = models.PositiveSmallIntegerField(choices=ROUTE_ACTION_CHOICES)
    app_status = models.ForeignKey("ApplicationStatus")
    #group=models.ForeignKey(Group)
    uid = models.CharField(max_length=50)
    
    class Meta:
        db_table = u'r_application_history'
        permissions=(
            ("add_app_history",u"添加申請單歷史"),
        )

'''
class Application(models.Model):
    app_id = models.CharField(max_length=20, primary_key=True)
    app_type = models.CharField(max_length=50)    #CARD  _INOUT
    class_type = models.CharField(max_length=50)
    #status = models.CharField(max_length=50)
    status = models.ForeignKey(AppStatus)
    route_name = models.CharField(max_length=50)
    
    submit_by = models.ForeignKey(User,related_name='submit') #申請單提交人(代申請)
    #applicant = models.ForeignKey(User,related_name='applicant') #申請人
    
    created_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    objects = ApplicationManager()

    #管製卡部份
    card_comment = models.TextField(null=True,blank=True)
    card_start_date =models.DateField(null=True,blank=True)
    card_end_date = models.DateField(null=True,blank=True)
    
    #攜入部份
    in_comment = models.TextField(blank=True)
    in_requested_date = models.DateField(null=True)  #申請攜入/攜出日期
    in_device_dest = models.CharField(max_length=50,blank=True)
    in_guard_by = models.CharField(max_length=50,blank=True)  #值班警衛
    in_guard_through_date =  models.DateTimeField(null=True) #攜入時間
    
    #攜出部份
    out_comment = models.TextField(blank=True)
    out_requested_date = models.DateField(null=True)  #申請攜入/攜出日期
    #device_dest = models.CharField(max_length=50)
    out_guard_by = models.CharField(max_length=50,blank=True)  #值班警衛
    out_guard_through_date =  models.DateTimeField(null=True) #攜入時間

    #設備信息
    owner = models.CharField(choices=OWNER_CHOICES,max_length=20,blank=True) #資產類別
    manufacturer = models.CharField(max_length=50)
    model_no = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    sn = models.CharField(max_length=50)
    lan_mac = models.CharField(max_length=17)
    wifi_mac = models.CharField(max_length=17,blank=True)
    
    #攜帶人/使用人 信息
    emp_no = models.CharField(max_length=20,blank=True)    #工號
    name = models.CharField(max_length=50)                 #姓名
    company = models.CharField(max_length=50,blank=True)   #公司
    grade = models.CharField(max_length=20,blank=True)     #資位
    position = models.CharField(max_length=20,blank=True)   #管理職
    extension = models.CharField(max_length=20,blank=True) #分機號
    telephone = models.CharField(max_length=20,blank=True) #聯繫電話
    id_type = models.CharField(choices=ID_CHOICES,max_length=20,blank=True)   #證件類型
    id_no  = models.CharField(max_length=30,blank=True)    #證件號碼
    
    id_image = models.ImageField(u'證件影印',upload_to='images/attchment/%Y-%m/')
    promise_image = models.ImageField(u'承諾書（含簽名檔）',upload_to='images/attchment/%Y-%m/')
    
    def __unicode__(self):
        return u'%s'% self.app_id
    class Meta:
        db_table = u'r_application'

class AppStatus(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return u'%s'% self.name
    class Meta:
        db_table = u'c_application_status'
        
class ApplicationCard(models.Model):
    CHOICE_GRADE = [ ( unicode(x.level),x.name ) for x in EmpGrade.objects.all()]
    
    application = models.ForeignKey(Application, primary_key=True)
    
    comment = models.TextField()

    start_date =models.DateField(null=True)
    end_date = models.DateField(null=True)
    
    owner = models.CharField(choices=OWNER_CHOICES,max_length=20,blank=True) #資產類別
    manufacturer = models.CharField(max_length=50)
    model_no = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    sn = models.CharField(max_length=50)
    lan_mac = models.CharField(max_length=17)
    wifi_mac = models.CharField(max_length=17,blank=True)
    
    #申請人信息
    emp_no = models.CharField(max_length=20,blank=True)    #工號
    name = models.CharField(max_length=50)                 #姓名
    company = models.CharField(max_length=50,blank=True)   #公司
    grade = models.CharField(max_length=20,blank=True,choices=CHOICE_GRADE)     #資位
    position = models.CharField(max_length=20,blank=True)   #管理職
    extension = models.CharField(max_length=20,blank=True) #分機號
    telephone = models.CharField(max_length=20,blank=True) #聯繫電話

    id_type = models.CharField(choices=ID_CHOICES,max_length=20,blank=True)   #證件類型
    id_no  = models.CharField(max_length=30,blank=True)    #證件號碼
    
    id_image = models.ImageField(u'證件影印',upload_to='images/attchment/%Y-%m/')
    promise_image = models.ImageField(u'承諾書（含簽名檔）',upload_to='images/attchment/%Y-%m/')
    
    def __unicode__(self):
        return u'%s'% self.application
    class Meta:
        db_table = u'r_application_card'

class ApplicationInOut(models.Model):
    application = models.ForeignKey(Application, primary_key=True)
    
    #攜入部份
    in_comment = models.TextField(blank=True)
    in_requested_date = models.DateField(null=True)  #申請攜入/攜出日期
    in_device_dest = models.CharField(max_length=50,blank=True)
    in_guard_by = models.CharField(max_length=50,blank=True)  #值班警衛
    in_guard_through_date =  models.DateTimeField(null=True) #攜入時間
    #攜出部份
    out_comment = models.TextField(blank=True)
    out_requested_date = models.DateField(null=True)  #申請攜入/攜出日期
    #device_dest = models.CharField(max_length=50)
    out_guard_by = models.CharField(max_length=50,blank=True)  #值班警衛
    out_guard_through_date =  models.DateTimeField(null=True) #攜入時間
    
    #created_date = models.DateTimeField(default=datetime.datetime.now)
    #modify_date = models.DateTimeField(default=datetime.datetime.now)

    owner = models.CharField(choices=OWNER_CHOICES,max_length=20,blank=True) #資產類別
    manufacturer = models.CharField(max_length=50)
    model_no = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    sn = models.CharField(max_length=50)
    lan_mac = models.CharField(max_length=17)
    wifi_mac = models.CharField(max_length=17,blank=True)
    
    #申請人信息
    emp_no = models.CharField(max_length=20,blank=True)    #工號
    name = models.CharField(max_length=50)                 #姓名
    company = models.CharField(max_length=50,blank=True)   #公司
    grade = models.CharField(max_length=20,blank=True)     #資位
    position = models.CharField(max_length=20,blank=True)   #管理職
    extension = models.CharField(max_length=20,blank=True) #分機號
    telephone = models.CharField(max_length=20,blank=True) #聯繫電話
    id_type = models.CharField(choices=ID_CHOICES,max_length=20,blank=True)   #證件類型
    id_no  = models.CharField(max_length=30,blank=True)    #證件號碼
    
    id_image = models.ImageField(u'證件影印',upload_to='images/attchment/%Y-%m/')
    promise_image = models.ImageField(u'承諾書（含簽名檔）',upload_to='images/attchment/%Y-%m/')
    
    def __unicode__(self):
        return u'%s'% self.application
    class Meta:
        db_table = u'r_application_in_out'

class Application(models.Model):
    app_no = models.CharField(max_length=20, unique=True)
    #app_type = models.IntegerField()#暫時取消
    guest = models.ForeignKey(Guest,null=True)#來訪客戶
    device = models.ForeignKey(Device)
    created_dt = models.DateTimeField(auto_now_add=True)#創建單日期

    def __unicode__(self):
        return u'%s'% self.app_no
        
    class Meta:
        db_table = u'r_application'
        #ordering = ['-createdt','-applyEmpId']

class App_Detail(models.Model):
    # app_no = models.OneToOneField(Application)
    TYPE_CHOICES = (
        (1, '攜入'),
        (2, '攜出'),
        (3, '管製卡(員工)'),
        (4, '管製卡(駐廠客戶)'),
        (5, '管製卡(客戶)'),
    )
    application = models.ForeignKey(Application,primary_key=True)
    app_type = models.IntegerField(choices=TYPE_CHOICES)# (in,out,card)
    applicant = models.ForeignKey(User)
    app_reason = models.TextField()#textfield
    requested_dt = models.DateField()#申請攜入.攜出日期
    device_dest = models.CharField(max_length=50,null=True)#申請設備所到地點
    bu_verified_by = models.CharField(max_length=50,null=True)#部級主管
    finally_approved_by=models.CharField(max_length=50,null=True)#授權主管
    buit_or_hr_verified_by =models.CharField(max_length=50,null=True)#資安幹事或者人資主管
    it_dept_verfied_by = models.CharField(max_length=50,null=True)
    it_dept_approved_by = models.CharField(max_length=50,null=True)
    disagreed_by = models.CharField(max_length=50,null=True,blank=True) #拒簽人
    disagree_reason = models.TextField(null=True)#拒簽原因
    through_guard_dt = models.DateTimeField(null=True)#警衛放行時間
    guard_verified_by = models.CharField(max_length=50,null=True)
    #out_date = models.DateField(auto_now=True)
    #
    def __unicode__(self):
        return u'%s'% self.reason
    class Meta:
        db_table = u'r_app_detail'
        unique_together = ('application', 'app_type')#利用此方式實現類似複合primary key

class ITSecurityCheck(models.Model):
    """攜出申請 IT資安檢查"""
    application = models.ForeignKey(Application,primary_key=True)
    checked_by = models.ForeignKey(User)
    comment = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'%s'% self.checked_note
    class Meta:
        db_table = u'r_it_security_check'

class Guest(models.Model):
    name = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    identify_type = models.CharField(max_length=20)
    identify_no  = models.CharField(max_length=30)
    
    def __unicode__(self):
        return u'%s'% self.name
    class Meta:
        db_table = u'r_guest'

class DeviceManager(models.Manager):
    def create_device(self,owner,manufacturer,model_no,color,sn,lan_mac,wifi_mac):
        device = self.model(owner=owner,manufacturer=manufacturer,model_no=model_no,
                            color=color,sn=sn,lan_mac=lan_mac,wifi_mac=wifi_mac)
        device.save()
        return device

class Device(models.Model):
    OWNER_CHOICES = (
        (1, 'Personal'),
        (2, 'Company'),
    )
    owner = models.IntegerField(choices=OWNER_CHOICES)#資產類別
    manufacturer = models.CharField(max_length=50)
    model_no = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    sn = models.CharField(max_length=50)
    lan_mac = models.CharField(max_length=17)
    wifi_mac = models.CharField(max_length=17,null=True)
    objects = DeviceManager()
    
    def __unicode__(self):
        return u'%s'% self.model_no
    class Meta:
        db_table = u'r_device'
'''


