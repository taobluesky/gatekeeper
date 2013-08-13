#coding:utf-8

# python imports
import os
import mimetypes
import stat
from urllib import unquote

# django imports
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from gatekeeper.core.utils import LazyEncoder
from django.utils import simplejson
from django.http import HttpResponse,CompatibleStreamingHttpResponse,Http404
from django.core.files import File
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.views.static import serve

# gatekeeper imports
from gatekeeper.account.models import Employee
    
@login_required
def home(request, template_name="core/home.html"):
    """
    主頁內容.
    """
    #print request.path
    return render_to_response(template_name, RequestContext(request, {
    }))

@login_required
def get_emp_info(request):
    if request.method == "GET":
        try:
            emp_no = request.GET.get("emp_no","")
            emp = Employee.objects.get(emp_no=emp_no)
            data = {"name":emp.name,
                    "notes_mail":emp.notes_mail,
                    "extension":emp.extension,
                    "telephone":emp.telephone,
                    "grade":emp.grade,
                    "position":emp.position,
                    "department":emp.department.name,
            }
            status = "success"
        except Exception,e:
            data ={}
            status = "failure"
    else:
        data={}
        status = "failure"
        
    result = simplejson.dumps({
        "data": data,
        "status": status,
    }, cls=LazyEncoder)
    return HttpResponse(result,mimetype='application/json')
    
def download_view(request, path, document_root=None, show_indexes=False):
    """
    下載 document_root 目錄裏面的文件(包括子目錄)
    """
    response = serve(request, path, document_root, show_indexes)
    newpath = path.replace('\\','/').rstrip('/')
    filename = newpath.split('/')[-1]
    response['Content-Disposition'] = 'attachment; filename="%s"'% filename
    return response
    
    