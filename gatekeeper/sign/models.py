from django.db import models

    
class User(models.Model):
    emp_no = models.CharField(max_length=10,primary_key=True)
    password = models.CharField(max_length=128,null=True,blank=True)
    department = models.CharField(max_length=50)
    #other
    def __unicode__(self):
        return u'%s'% self.emp_no
    class Meta:
        db_table = u'c_user'
        
class Guest(models.Model):
    #application = models.ForeignKey(Application)#爲了讓客戶可以被多個申請單使用,不為主鍵
    name = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    identify_type = models.CharField(max_length=20)
    identify_no  = models.CharField(max_length=30)
    
    def __unicode__(self):
        return u'%s'% self.name
    class Meta:
        db_table = u'r_guest'


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

    def __unicode__(self):
        return u'%s'% self.model_no
    class Meta:
        db_table = u'r_device'
        
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
        (3, '管製卡'),
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
    application = models.ForeignKey(Application,primary_key=True)
    checked_by = models.ForeignKey(User)
    checked_note = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'%s'% self.checked_note
    class Meta:
        db_table = u'r_it_security_check'
    