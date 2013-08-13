# -*- coding: utf-8 -*-

#django imports
from django.contrib import admin

#gatekeeper imports
from .models import ApplicationStatus,RouteHeader,SignatureRoute
from .models import ApplicationAuth
from .models import ApplicationBase
from .models import ApplicationCard
from .models import ApplicationIn
from .models import ApplicationOut
from .models import ApplicationHistory
from .models import ApplicationCarry

class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'display_name','signer_label','time_label')
    
class RouteHeaderAdmin(admin.ModelAdmin):
    list_display = ('route_name','header')
    
class SignatureRouteAdmin(admin.ModelAdmin):
    list_display = ('id','route_name','group','action','app_status','next_route')
    
class ApplicationAuthAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(ApplicationStatus,ApplicationStatusAdmin)
admin.site.register(RouteHeader,RouteHeaderAdmin)
admin.site.register(SignatureRoute,SignatureRouteAdmin)
admin.site.register(ApplicationAuth,ApplicationAuthAdmin)
admin.site.register(ApplicationBase)
admin.site.register(ApplicationCarry)
admin.site.register(ApplicationCard)
admin.site.register(ApplicationIn)
admin.site.register(ApplicationOut)
admin.site.register(ApplicationHistory)