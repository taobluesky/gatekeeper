# -*- coding: utf-8 -*-
import datetime
from warnings import warn
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from gatekeeper.auth.signals import user_logged_in, user_logged_out
from models import User,check_password

SESSION_KEY = '_auth_user_id'
ADDR_SESSION_KEY = '_auth_user_ip'
#BACKEND_SESSION_KEY = '_auth_user_backend'
#REDIRECT_FIELD_NAME = 'next'

def authenticate(**credentials):
    """
    如果所給的認證信息有效,成功返回User對象,失敗返回None.
    """
    try:
        db_user = User.objects.get(username=credentials['username'])
        if db_user and check_password(credentials['password'],db_user.password):
            user = db_user
        else:
            user = None
    except User.DoesNotExist:
        user = None
    return user

def login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
    
    # TODO: It would be nice to support different login methods, like signed cookies.
    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            if _auth_user_ip(request):
                request.session.flush()
            else:
                request.session.create()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = user.id
    request.session[ADDR_SESSION_KEY] = request.META.get('REMOTE_ADDR','')
    #request.session[BACKEND_SESSION_KEY] = user.backend
    if hasattr(request, 'user'):
        request.user = user
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    
def logout(request):
    """
    移除request中已被驗證的user's ID,并刷新request session.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        user = None
    # 合法用戶才能允許登出
    if _auth_user_ip(request):
        user_logged_out.send(sender=user.__class__, request=request, user=user)

        request.session.flush()
        if hasattr(request, 'user'):
            from gatekeeper.auth.models import AnonymousUser
            request.user = AnonymousUser()

def get_user(request):
    from gatekeeper.auth.models import AnonymousUser
    try:
        user_id = request.session[SESSION_KEY]
        #backend_path = request.session[BACKEND_SESSION_KEY]
        #backend = load_backend(backend_path)
        
        if _auth_user_ip(request):
            user = User.objects.get(pk=user_id)
        else:
            user = AnonymousUser()
            print('danger user!')
        #user = User.objects.get(pk=user_id) or AnonymousUser()
    except KeyError:
        user = AnonymousUser()
    return user

def _auth_user_ip(request):
    # 驗證 session key 是否屬於遠端用戶
    session_remote_addr = request.session.get(ADDR_SESSION_KEY,'')
    if session_remote_addr == request.META.get('REMOTE_ADDR',''):
        return True
    else:
        return False
        