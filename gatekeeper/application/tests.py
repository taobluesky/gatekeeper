#-*-coding:utf-8-*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class MacFieldTest(TestCase):
    def setUp(self):
        pass
        
    def test_mac_field_validator(self):
        from gatekeeper.application.fields import MacField
        self.assertFieldOutput(MacField, 
            valid = {
                'aa-bb-cc-dd-ee-ff': 'aa-bb-cc-dd-ee-ff',
                '1f-f0-11-b4-a2-4c': '1f-f0-11-b4-a2-4c',
            }, 
            invalid = {
                'aa:bb:cc:dd:ee:ff': [u"MAC地址格式有誤."],
                '1z-f0-11-b4-a2-4c': [u"MAC地址格式有誤."],
                '19-s0-d1-f4-gg-4c': [u"MAC地址格式有誤."],
                'aaa': [u"MAC地址格式有誤."],
            },
            empty_value=u'',
        )
        
class DeviceFormTest(TestCase):
    def test_form(self):
        from .forms import DeviceForm_
        form = DeviceForm_(data={
            "owner":0,
            "manufacturer":0,
            "model_no":'aaa',
            "color":0,
            "sn":"xxxx",
            "lan_mac":"aa-bb-cc-dd-ee-ff",
            "wifi_mac":"",
            "applicant_type":0,
        })
        #print unicode(form.fields)
        #print unicode(form.errors)
        form.save()
        self.assertEqual(form.is_valid(), True)
        
class AppCarryFormTest(TestCase):
    def test_form(self):
        from .forms import AppCarry
        form = AppCarry(data={
            "owner":0,
            "manufacturer":0,
            "model_no":'aaa',
            "color":0,
            "sn":"xxxx",
            "lan_mac":"aa-bb-cc-dd-ee-ff",
            "wifi_mac":"",
            "applicant_type":0,
        })
        print unicode(form.fields)
        print unicode(form.errors)
        form.save()
        self.assertEqual(form.is_valid(), True)