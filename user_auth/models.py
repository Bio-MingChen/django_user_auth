from datetime import datetime,timedelta
import hashlib
import string
import os

from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings 
# Create your models here.

class UserAuth(models.Model):
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    activation_time = models.DateTimeField(default=datetime.now())

    activation_key = models.CharField(max_length=64,blank=True)

    activation_valid = models.BooleanField(default=False)

    def __str__(self):
        return self.user

    def generate_activation_key(self,save=True):
        """
        生成64位随机激活码
        """
        random_string = get_random_string(length=32,allowed_chars=string.printable)
        self.activation_key = hashlib.sha256(random_string.encode('utf-8')).hexdigest()

        if save:
            self.save()

        return self.activation_key

    def send_activation_email(self,request,purpose='reset_password'):
        """
        用于给用户发送注册确认邮件或者密码重置激活邮件
        purpose = [ reset_password,registration ]
        这里特别需要注意的是activation_url的构建
        purpose的设置是以urls.py中设置的路径关联的
        因为在urls.py中设置了激活URL为：
        resent_password/activation/(P<activation_key>[\w-]+)
        registration/activation/(P<activation_key>[\w-]+)
        因此，这里我拼了一个这样的激活路径,如果后续修改了url，那么
        这里的activation_url也必须要修改以适应新的激活URL
        """
        activation_key = self.generate_activation_key(save=True)
        activation_url = 'http://' + "/".join([request.META['HTTP_HOST'],
                'accounts',purpose,'activation',activation_key])
        if purpose == 'registration':
            subject = getattr(settings,'REGISTRATION_SUBJECT')
            message = getattr(settings,'REGISTRATION_MESSAGE')
        elif purpose == 'reset_password':
            subject = getattr(settings,'RESET_PASSWORD_SUBJECT')
            message = getattr(settings,'RESET_PASSWORD_MESSAGE')
        if subject and message:
            message = message.format(
                username=self.user.username,
                activation_url=activation_url,
                sender=getattr(settings,'EMAIL_HOST_USER'),
                time=datetime.now())

        from_email = getattr(settings,'DEFAULT_FROM_EMAIL')
        recipient_list = [ self.user.email ]
        send_mail(subject,message,from_email,recipient_list)
        #保存发送激活码时间
        self.activation_time = datetime.now()
        self.activation_valid = True
        self.save()
        return True
    
    def confirm_activation_key(self):
        """
        确认激活码是否有效且验证时间未过期
        这里特别需要说明的是activation_valid值
        它主要是用来保证用户激活及密码重置以后
        原来的激活或者密码重置界面将无法使用
        默认情况下是false
        """
        expired_days = getattr(settings,'EXPIRED_DAYS') or 1
        is_not_expired = self.activation_time + timedelta(expired_days) > datetime.now()
        is_valid = self.activation_valid
        return is_valid and is_not_expired
    
