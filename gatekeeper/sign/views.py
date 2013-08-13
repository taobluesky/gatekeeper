# Create your views here.
import time,re
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.template.context import RequestContext
from gatekeeper.sign.models import *
from sign.forms import *
from django.core import serializers
import json

def create_app(request):
    if not request.POST:
        form =  DeviceForm()
    else:
        form =  DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('ok')

    return render_to_response('deviceform.html',{'form':form},
                                  context_instance=RequestContext(request))

def test(request):
    #print request.raw_post_data
    data = serializers.serialize("json",Device.objects.all())
    response = HttpResponse(data)
    return response
    
def json_device(request):
    return render_to_response('test.html')

def testajax(request):
    #return render_to_response('test.html')
    return render_to_response('test1.html')

def wizard(request):
    step_number = request.POST["step_number"]
    #print request.POST
            
    if step_number == '1':
        return render_to_response('wizard_step1.html')
    elif step_number == '2':
        #request.session["step1"]=request.POST
        stepform = request.session["step2"]
        print stepform
        if not stepform:
            form = DeviceForm(stepform)
        else:
            form =  DeviceForm()
        return render_to_response('wizard_step2.html',{'form':form})
    elif step_number == '3':
        #post = request.POST
        #post.pop("step_number")
        request.session["step2"] = {}
        return HttpResponse("ok")
    #return render_to_response('deviceform.html',{'form':form},
    #                              context_instance=RequestContext(request))
    #step_number = request.POST("step_number")
    #print step_number
    #if step_number==1:
    #    return render_to_response('wizard_step1.html')
    #elif step_number ==2:
    #    return render_to_response('wizard_step2.html',{'form':form})
        
    #return render_to_response('test.html')
    #return render_to_response('wizard.html')

def wizard1(request):
    #return render_to_response('test.html')
    return render_to_response('wizard_step1.html')
    
def wizard2(request):
    #return render_to_response('test.html')
    form =  DeviceForm()
    return render_to_response('wizard_step2.html',{'form':form})
    
def wizardtest(request):
    return render_to_response('wizard_test.html')
    
def jsonsave(request):
    if request.is_ajax():
        if request.method == 'POST':
            print request.POST["wifi_mac"]
            #print request.POST
            #print request.raw_post_data
            #form =  DeviceForm(request.POST)
            #if form.is_valid():
            #    form.save()
            #else:
            #    print 'fail'
            return HttpResponse(json.dumps({"status": "success"}),
                    mimetype='application/json')
   