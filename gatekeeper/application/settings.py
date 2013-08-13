#-*-coding:utf-8-*-

#django imports
from django.utils.translation import ugettext_lazy as _

#   type_code route_name app_name
APP_TYPE_ROUTE_NAME =(
    ('CARRY_IN_EMP','CARRY_IN',_(u'攜入申請單')),
    ('CARRY_IN_CUSTOMER','CARRY_IN',_(u'攜入申請單')),
    ('CARRY_OUT_EMP','CARRY_OUT',_(u'攜出申請單')),
    ('CARRY_OUT_CUSTOMER','CARRY_OUT',_(u'攜出申請單')),
    ('CARRY_INOUT_EMP','CARRY_INOUT',_(u'攜入攜出申請單')),
    ('CARRY_INOUT_CUSTOMER','CARRY_INOUT',_(u'攜入攜出申請單')),
    ('CARD_EMP','CARD_EMP',_(u'管製卡(員工)申請單')),
    ('CARD_CUSTOMER','CARD_CUSTOMER',_(u'管製卡(客戶)申請單')),
    ('CARD_CUSTOMER_ONSITE','CARD_CUSTOMER_ONSITE',_(u'管製卡(駐廠客戶)申請單')),
)

APP_TYPE_CARRY_INOUT = 0
APP_TYPE_CARRY_IN = 1
APP_TYPE_CARRY_OUT = 2
APP_TYPE_CARD_EMP = 3
APP_TYPE_CARD_CUSTOMER = 4
APP_TYPE_CARD_CUSTOMER_ONSITE = 5

APP_TYPE_CHOICES =(
    (APP_TYPE_CARRY_INOUT,u"資訊類物品攜入攜出申請"),
    (APP_TYPE_CARRY_IN,u"資訊類物品攜入申請"),
    (APP_TYPE_CARRY_OUT,u"資訊類物品攜出申請"),
    (APP_TYPE_CARD_EMP,u"管製卡員工專用"),
    (APP_TYPE_CARD_CUSTOMER,u"管製卡客戶專用"),
    (APP_TYPE_CARD_CUSTOMER_ONSITE,u"管製卡駐廠客戶專用"),
)

APPLICANT_TYPE_CUSTOMER = '0'
APPLICANT_TYPE_EMPLOYEE = '1'
CARRY_APPLICANT_TYPE_CHOICES =(
    (APPLICANT_TYPE_CUSTOMER,u"來訪人/客戶"),
    (APPLICANT_TYPE_EMPLOYEE,u"集團員工"),
)

MANUFACTURER_CHOICES=(
    (0,u"Apple"),
    (1,u"DELL"),
    (2,u"HP"),
    (3,u"其它品牌"),
)

COLOR_CHOICES=(
    (0,u"白色"),
    (1,u"黑色"),
    (2,u"其它顏色"),
)

OWNER_CHOICES_COMPANY = 0
OWNER_CHOICES_PERSONAL = 1

OWNER_CHOICES=(
    (OWNER_CHOICES_COMPANY,u"公司資產"),
    (OWNER_CHOICES_PERSONAL,u"個人資產"),
)

ID_CHOICES=(
    (0,u'身份證'),
    (1,u'公司廠牌'),
)

APP_STATUS_SUBMIT = 0
APP_STATUS_DEPARTMENT_CHECK = 1
APP_STATUS_DEPARTMENT_APPROVE = 2
APP_STATUS_IT_CHECK = 3
APP_STATUS_IT_APPROVE = 4
APP_STATUS_HR_APPROVE = 5
APP_STATUS_SPECIAL_APPROVE = 6
APP_STATUS_MAKE_CARD = 7
APP_STATUS_CLOSED = 8
APP_STATUS_REJECTED = 10

APP_STATUS_IN_DEPARTMENT_CHECK = 11
APP_STATUS_OUT_DEPARTMENT_CHECK = 21
APP_STATUS_IN_DEPARTMENT_APPROVE = 22
APP_STATUS_OUT_DEPARTMENT_APPROVE = 12
APP_STATUS_IN_SECRETARY_CHECK = 9
APP_STATUS_OUT_SECRETARY_CHECK = 13
APP_STATUS_IN_IT_CHECK = 14
APP_STATUS_OUT_IT_CHECK = 15
APP_STATUS_IN_IT_APPROVE = 16
APP_STATUS_OUT_IT_APPROVE = 17
APP_STATUS_IN_GUARD_CHECK = 18
APP_STATUS_OUT_GUARD_CHECK = 19
APP_STATUS_IT_INSPECT = 20
APP_STATUS_IT_REINSPECT = 23

APP_STATUS_NAME_CHOICES =(
    (APP_STATUS_SUBMIT,u"用戶提交"),
    (APP_STATUS_DEPARTMENT_CHECK,u"部門審核"),
    (APP_STATUS_DEPARTMENT_APPROVE,u"部門核准"),
    (APP_STATUS_IT_CHECK,u"資訊審核"),
    (APP_STATUS_IT_APPROVE,u"資訊核准"),
    (APP_STATUS_HR_APPROVE,u"人資核實"),
    (APP_STATUS_SPECIAL_APPROVE,u"特批核准"),
    (APP_STATUS_MAKE_CARD,u"資訊製卡"),
    (APP_STATUS_CLOSED,u"關閉申請"),
    (APP_STATUS_REJECTED,u"申請被拒"),
    
    (APP_STATUS_IN_DEPARTMENT_CHECK,u"部門審核_攜入_"),
    (APP_STATUS_OUT_DEPARTMENT_CHECK,u"部門審核_攜出_"),
    (APP_STATUS_IN_DEPARTMENT_APPROVE,u"部門核准_攜入_"),
    (APP_STATUS_OUT_DEPARTMENT_APPROVE,u"部門核准_攜出_"),
    (APP_STATUS_IN_SECRETARY_CHECK,u"資安幹事審核_攜入_"),
    (APP_STATUS_OUT_SECRETARY_CHECK,u"資安幹事審核_攜出_"),
    (APP_STATUS_IN_IT_CHECK,u"資訊審核_攜入_"),
    (APP_STATUS_OUT_IT_CHECK,u"資訊審核_攜出_"),
    (APP_STATUS_IN_IT_APPROVE,u"資訊核准_攜入_"),
    (APP_STATUS_OUT_IT_APPROVE,u"資訊核准_攜出_"),
    (APP_STATUS_IN_GUARD_CHECK,u"門警檢查_攜入_"),
    (APP_STATUS_OUT_GUARD_CHECK,u"門警檢查_攜出_"),
    (APP_STATUS_IT_INSPECT,u"資安設備檢查"),
    
    (APP_STATUS_IT_REINSPECT,u"資安設備複檢"),
)

APP_STATUS_DISPLAYNAME_CHOICES =(
    (0,u"用戶提交"),
    (1,u"部門審核"),
    (2,u"部門核准"),
    (3,u"資訊審核"),
    (4,u"資訊核准"),
    (5,u"人資核實"),
    (6,u"特批核准"),
    (7,u"資訊製卡"),
    (8,u"關閉申請"),
    (9,u"申請被拒"),
    (10,u"資安幹事審核"),
    (11,u"資安設備檢查"),
    (12,u"門警檢查"),
    (13,u"資安設備複檢"),
    
)

APP_STATUS_SINGER_LABEL_CHOICES=(
    (0,u"部門主管"),
    (1,u"資安幹事"),
    (2,u"核准主管"),
    (3,u"人資核實"),
    (4,u"資安常委"),
    (5,u"資安主委"),
    (6,u"值班警衛"),
    (7,u"申請人"),
    (8,u"製卡人員"),
    (9,u"資安總幹事"),
)

APP_STATUS_TIME_LABEL_CHOICES=(
    (0,u"提交時間"),
    #(1,u"退回時間"),
    (1,u"審核時間"),
    (2,u"核准時間"),
    (3,u"完成時間"),
)

ROUTE_ACTION_AGREE = 0
ROUTE_ACTION_REJECT = 1
ROUTE_ACTION_DONE = 2
ROUTE_ACTION_SUBMIT = 3
ROUTE_ACTION_CHOICES=(
    (ROUTE_ACTION_AGREE,u"AGREE"),
    (ROUTE_ACTION_REJECT,u"REJECT"),
    (ROUTE_ACTION_DONE,u"DONE"),
    (ROUTE_ACTION_SUBMIT,u"SUBMIT"),
)