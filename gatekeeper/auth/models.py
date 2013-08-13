# -*- coding: utf-8 -*-
import datetime
import urllib

from django.db import models
from django.utils.encoding import smart_str
#from django.utils.hashcompat import md5_constructor, sha_constructor
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import constant_time_compare

UNUSABLE_PASSWORD = '!' # This will never be a valid hash

def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return constant_time_compare(hsh, get_hexdigest(algo, salt, raw_password))

class Permission(models.Model):
    name = models.CharField(_('name'), max_length=50)
    codename = models.CharField(_('codename'), max_length=100)
    #content_type = models.ForeignKey(ContentType)
    #objects = PermissionManager()
    
    class Meta:
        db_table = u'c_permission'
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        #unique_together = (('content_type', 'codename'),)
        #ordering = ('content_type__app_label', 'content_type__model', 'codename')

    def __unicode__(self):
        return u"%s" % (
            #unicode(self.content_type.app_label),
            #unicode(self.content_type),
            unicode(self.name))

class Role(models.Model):
    name = models.CharField(max_length=50)
    role_permission = models.ManyToManyField(Permission,blank=True)
    
    class Meta:
        db_table = u'c_role'
   
    def __unicode__(self):
        return u'%s' %(self.name)
        
class UserManager(models.Manager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given username, e-mail and password.
        """
        now = datetime.datetime.now()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        try:
            email_name, domain_part = email.strip().split('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])

        user = self.model(username=username, email=email, is_staff=False,
                         is_active=True, is_superuser=False, last_login=now,
                         date_joined=now)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        u = self.create_user(username, email, password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])

class User(models.Model):
    username = models.CharField(_('user name'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters"))
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('e-mail address'), blank=True)
    password = models.CharField(_('password'), max_length=128, help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_("Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(_('active'), default=True, help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."))
    is_superuser = models.BooleanField(_('superuser status'), default=False, help_text=_("Designates that this user has all permissions without explicitly assigning them."))
    last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    date_joined = models.DateTimeField(_('date joined'), default=datetime.datetime.now)
    role = models.ManyToManyField(Role)
    #groups = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True,
    #    help_text=_("In addition to the permissions manually assigned, this user will also get all permissions granted to each group he/she is in."))
    #user_permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), blank=True)
    objects = UserManager()

    class Meta:
        db_table = u'c_user'
        #verbose_name = _('user')
        #verbose_name_plural = _('users')
        
    def __unicode__(self):
        return self.username

    def set_password(self, raw_password):
        if raw_password is None:
            self.set_unusable_password()
        else:
            import random
            algo = 'sha1'
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, raw_password)
            self.password = '%s$%s$%s' % (algo, salt, hsh)
            
    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD
        
    def is_authenticated(self):
        """
        一直返回True. 告訴用戶已經驗證過.
        """
        return True

# TODO:消息模型只是初步確定,後續還需更改.
class Message(models.Model):
    user = models.ForeignKey(User, related_name='_message_set')
    message = models.TextField(_('message'))
    type = models.IntegerField()
    class Meta:
        db_table = u'r_user_message'
    def __unicode__(self):
        return self.message

class AnonymousUser(object):
    id = None
    username = ''
    
    def __init__(self):
        pass
        
    def is_authenticated(self):
        return False
        