# -*- coding: utf-8 -*-

#python imports
#import json
import datetime
import urllib

# django imports
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode

class LazyEncoder(simplejson.JSONEncoder):
    """Encodes django's lazy i18n strings.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj
        
def set_message_cookie(msg, response=None, url=''):
    """Returns a HttpResponseRedirect object with passed url and set cookie
    ``message`` with passed message.
    """
    # We just keep the message two seconds.
    max_age = 2
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() +
        datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    if url != '':
        response = HttpResponseRedirect(url)
    response.set_cookie("message", gk_quote(msg), max_age=max_age, expires=expires)

    return response

    
def gk_quote(string, encoding="utf-8"):
    """Encodes passed string to passed encoding before quoting with
    urllib.quote().
    """
    return urllib.quote(string.encode(encoding))
    