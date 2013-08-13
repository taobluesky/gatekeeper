#-*-coding:utf-8-*-

#python imports
import re

#django imports
from django.forms.fields import CharField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

mac_re = re.compile(r'^[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}-[A-Fa-f0-9]{2}$')
validate_mac = RegexValidator(mac_re, _(u"MAC地址格式有誤。"), 'invalid')

class MacField(CharField):
    """
    自定義 MAC地址的Field
    """
    default_error_messages = {
        'invalid': _(u"MAC地址格式有誤。"),
    }
    default_validators = [validate_mac]

    def clean(self, value):
        value = self.to_python(value).strip()
        return super(MacField, self).clean(value)
        


