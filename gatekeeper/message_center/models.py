#-*-coding:utf-8-*-

#django imports 
from django.db import models
from django.contrib.auth.models import User


class NotificationMessage(models.Model):
    """消息中心
    """
    user = models.ForeignKey(User)
    title = models.CharField(max_length=256)
    content = models.TextField()
    is_delete = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    post_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = u'r_notification_message'