# -*- coding: utf-8 -*-

# django imports
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.db.models import Q

# gk imports
from gatekeeper.account.models import Employee,Organization,SignedMember
from gatekeeper.core.utils import LazyEncoder
from gatekeeper.management.forms import SignerForm,MemberModelForm

def gen_tree(root=None):
    org_tree =[]
    
    if root is None:
        org_query = Organization.objects.filter(parent='NULL')
    else:
        org_query = Organization.objects.filter(parent=root["id"])
        
    if not org_query :
        return
        
    for org in org_query:
        
        if root is None:
            
            next_root = {"id":org.uuid,"text":org.name,"state":"closed"}
            #print next_root
            #f.writelines(unicode(next_root))
            #f.writelines('\n')
            #org_dict.update({"uuid":org.uuid,"leaf":leaf})
            org_tree.append(next_root)
            gen_tree(root=next_root)
        else:
            #print root['name']
            next_root = {"id":org.uuid,"text":org.name}
            #print root
            
            #f.writelines('\n')
            #org_dict.update({"uuid":org.uuid,"leaf":leaf})
            if root.has_key("children"):
                root["children"].append(next_root)
            else:
                root.update({"children":[next_root]})
            
            #f.writelines(unicode(root))
            #f.writelines('\n')
            gen_tree(root=next_root)
    
    #f.flush()
    return org_tree
    
def has_child(parent):
    count = Organization.objects.filter(parent=parent).count()
    return True if count>0 else False
    
def get_org_node(parent=None):
    org_node_list=[]
    org_query = Organization.objects.filter(parent=parent)
    #url = reverse("gk_org_node",{"uuid":org.uuid})
    for org in org_query:
        node = {
            "id":org.uuid,
            "text":org.name,
            "state":"closed" if has_child(org.uuid) else 'open',
            #"attributes":{
            #    "url":reverse("gk_org_node"),
            #}
        }
        org_node_list.append(node)
        
    return org_node_list
    
    
def org_node(request):
    uuid =request.POST.get('id','NULL')
    print uuid
    r = get_org_node(uuid)
    #org_json = json.dumps(r)
    result = simplejson.dumps(r, cls=LazyEncoder)
    return HttpResponse(result,mimetype='application/json')
    
def org_tree(request):
    r = gen_tree()
    
    org_json = json.dumps(r)
    return HttpResponse(org_json,mimetype='application/json')
    #return JsonResponse(r)
    
def org_manage(request,template_name= 'management/manage_org.html'):
    #from application.models import gen_tree
    #r = gen_tree()
    #return HttpResponse(str(r))
    add_signer_html = add_signer_inline(request)
    add_member_html = add_member_inline(request)
    return render_to_response(template_name,RequestContext(request,{
        "add_signer_inline":add_signer_html,
        "add_member_inline":add_member_html,
    }))

def add_signer_inline(request,signer_form=None,template_name='management/add_signer_form.html'):
    if signer_form is None:
        signer_form = SignerForm()
    return render_to_string(template_name,{'form':signer_form})

def add_signer(request):
    if request.POST:
        signer_form = SignerForm(request.POST)
    else:
        signer_form = SignerForm()
        
    if signer_form.is_valid():
        pass
        cleaned_data = signer_form.cleaned_data
        emp = Employee.objects.get(emp_no= cleaned_data["emp_no"])
        org = Organization.objects.get(uuid=request.POST.get('department'))
        new_signer = SignedMember(
            department=org,
            employee=emp,
            group=cleaned_data["group"]
        )
        new_signer.save()
        status = "success"
    else:
        status = "failure"
        
    result = simplejson.dumps({
        "status":status,
        "html":add_signer_inline(request,signer_form),
    }, cls=LazyEncoder)
    return HttpResponse(result,mimetype='application/json')
    
def remove_signer(request):
    if request.POST:
        id_list = request.POST.get("id_list","").split(",")
        SignedMember.objects.filter(id__in=id_list).delete()
        status = "success"
    else:
        status = "failure"
    
    result = simplejson.dumps({
        "status":status,
    }, cls=LazyEncoder)
    return HttpResponse(result,mimetype='application/json')
    
def get_node_member(request):
    if request.method =='POST':
        department = request.POST.get('department','unknown')
        order = request.POST.get('order','asc')
        page = request.POST.get('page','1')
        rows = request.POST.get('rows','20')
        sort = request.POST.get('sort','emp_no')
        if order =='desc':
            order_str = '-'+sort
        elif order == 'asc':
            order_str = sort
        offset = (int(page)-1)*int(rows)
        end = offset + int(rows)
        total = Employee.objects.filter(department=department).count()
        member_list = Employee.objects.filter(department=department).order_by(order_str)[offset:end]
        row_list = []
        for member in member_list:
            row = {
                "emp_no":member.emp_no,
                "name":member.name,
                "notes_mail":member.notes_mail,
                "extension":member.extension,
                "telephone":member.telephone,
                "grade":member.grade,
                "position":member.position,
            }
            row_list.append(row)
            
        result = simplejson.dumps({
            "total":total,
            "rows":row_list,
        }, cls=LazyEncoder)
        return HttpResponse(result,mimetype='application/json')
    return

def get_node_signer_member(request):
    if request.method =='POST':
        department = request.POST.get('department','unknown')
        order = request.POST.get('order','asc')
        page = request.POST.get('page','1')
        rows = request.POST.get('rows','20')
        sort = request.POST.get('sort','employee')
        if order =='desc':
            order_str = '-'+sort
        elif order == 'asc':
            order_str = sort
        offset = (int(page)-1)*int(rows)
        end = offset + int(rows)
        total = SignedMember.objects.filter(department=department).count()
        member_list = SignedMember.objects.filter(department=department).order_by(order_str)[offset:end]
        row_list = []
        for member in member_list:
            employee = member.employee
            row = {
                "id":member.id,
                "employee":employee.emp_no,
                "name":employee.name,
                "role":member.group.name,
                "notes_mail":employee.notes_mail,
                "extension":employee.extension,
                "telephone":employee.telephone,
                "grade":employee.grade,
                "position":employee.position,
            }
            row_list.append(row)
            
        result = simplejson.dumps({
            "total":total,
            "rows":row_list,
        }, cls=LazyEncoder)
        return HttpResponse(result,mimetype='application/json')
    return
    
def search_member(request):
    if request.method =='POST':
        emp_no = request.POST.get('emp_no','')
        name = request.POST.get('name','')
        #order = request.POST.get('order','asc')
        page = request.POST.get('page','1')
        rows = request.POST.get('rows','20')
        #sort = request.POST.get('sort','emp_no')
        #if order =='desc':
        #    order_str = '-'+sort
        #elif order == 'asc':
        #    order_str = sort
        offset = (int(page)-1)*int(rows)
        end = offset + int(rows)
        filters = Q()
        if emp_no:
            filters &= Q(emp_no__icontains=emp_no) 
        if name :
            filters &= Q(name__icontains=name)
        
        #print filters
        total = Employee.objects.filter(filters).count()
        member_list = Employee.objects.filter(filters)[offset:end]
        row_list = []
        for member in member_list:
            department_str=''
            if member.department:
                from application.models import get_department_tree
                d_tree = get_department_tree(department=member.department)
                d_tree.reverse()
                
                department_str = '|'.join([node.name for node in d_tree])
                    
            row = {
                "emp_no":member.emp_no,
                "name":member.name,
                "department":department_str,
                "notes_mail":member.notes_mail,
                "extension":member.extension,
                "telephone":member.telephone,
                "grade":member.grade,
                "position":member.position,
            }
            row_list.append(row)

        result = simplejson.dumps({
            "total":total,
            "rows":row_list,
        }, cls=LazyEncoder)
        return HttpResponse(result,mimetype='application/json')
        
def move_member(request):
    if request.POST:
        id_list = request.POST.get("id_list","").split(",")
        department_id = request.POST.get("department",'')
        org = Organization.objects.filter(uuid=department_id)
        if org:
            Employee.objects.filter(emp_no__in=id_list).update(department=org[0])
        status = "success"
    else:
        status = "failure"
    
    result = simplejson.dumps({
        "status":status,
    }, cls=LazyEncoder)
    return HttpResponse(result,mimetype='application/json')

def add_member_inline(request,member_form=None,template_name='management/add_member_form.html'):
    #if request.POST:
    #    signer_form = MemberForm(request.POST)
    if member_form is None:
        member_form = MemberModelForm()
    return render_to_string(template_name,{'form':member_form})
    
def add_member(request):
    if request.POST:
        member_form = MemberModelForm(request.POST)
    else:
        member_form = MemberModelForm()
        
    if member_form.is_valid():
        cleaned_data = member_form.cleaned_data
        
        member = member_form.save(commit=False)
        member.department = cleaned_data["department"]
        member.save()
        
        #TODO:
        status = "success"
    else:
        status = "failure"
        
    result = simplejson.dumps({
        "status":status,
        "html":add_member_inline(request,member_form),
    }, cls=LazyEncoder)
    return HttpResponse(result,mimetype='application/json')
