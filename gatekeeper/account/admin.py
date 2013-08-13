# -*- coding: utf-8 -*-

#django imports
from django.contrib import admin

#gatekeeper imports
from gatekeeper.account.models import Department
from gatekeeper.account.models import Employee


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'has_layers')
    
admin.site.register(Department,DepartmentAdmin)
admin.site.register(Employee)