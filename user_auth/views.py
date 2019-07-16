import os

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponse,Http404
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.mail import send_mail

from .forms import Send_Email_Form,Registration_Form,Reset_Password_Form,Login_Form
from .models import UserAuth

# Create your views here.
def index(request):
    """
    这是首页视图
    """
    # return HttpResponse('This is index page!')
    # send_mail('test','test','chenming@novogene.com',['864606804@qq.com'])
    # print(request.META)
    return render(request,'user_auth/index.html',{})

def login_page(request):
    """
    登陆页面
    """
    error_message = ''
    if request.method == 'POST':
        form = Login_Form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username,password=password)
 
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('user_auth:index'))
            else:
                error_message = '用户名或密码错误！'
    else:
        form = Login_Form()

    return render(request,'user_auth/login.html',{'form':form,'error_message':error_message})

@login_required()
def logout_page(request):
    """
    登出页面
    """
    logout(request)
    return redirect(reverse('user_auth:index'))

def user_auth_registration(request):
    """
    管理用户注册页面
    """   

    if request.method == 'POST':
        # for i in User.objects.all(): #测试用，先清空用户
        #     i.delete()
        form = Registration_Form(request.POST)
        if form.is_valid():
            userform = form.save(commit=False)
            userform.is_active = False #初始用户未激活
            userform.save()

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            user = User.objects.get(username=username)
            user.set_password(user.password) #formmodel保存时不会自动加密，因此这里需要手动加密
            user.userauth = UserAuth(user=user)
            user.save()
            user.userauth.send_activation_email(request,purpose='registration')
            return render(request,'user_auth/registration_complete.html',{'username':username,
            'email':email})
        else:
            print(form.errors)
            return render(request,'user_auth/registration.html',{'form':form})
            
    form = Registration_Form()
    return render(request,'user_auth/registration.html',{'form':form}) 

def resend_activation_email(request,username,email):
    """
    重新发送激活邮件
    """
    user = User.objects.get(username=username,email=email)
    if user:
        user.userauth.send_activation_email(request,purpose='registration')
        return HttpResponse('邮件发送成功！')
    else:
        Http404('用户异常，请联系管理员')

def user_auth_send_email(request):
    """
    用于给重置密码的请求发送邮件
    """

    if request.method == 'POST':
        form = Send_Email_Form(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            user.userauth.send_activation_email(request)
            return HttpResponse('邮件已经发送，请登陆邮箱查收邮件')
    else:
        form = Send_Email_Form()
    
    return render(request,'user_auth/send_email.html',{'form':form})
    
def user_auth_activation(request,raw_activation_key=None):
    """
    用于激活用户
    """
    user = User.objects.get(userauth__activation_key=raw_activation_key)
    is_valid = user.userauth.confirm_activation_key()
    if user and is_valid:
        user.is_active = True
        user.userauth.activation_valid = False
        user.save()
        return render(request,'user_auth/activation_complete.html',{})
    
    elif user and user.is_active:
        return Http404('用户已经激活，请勿重复激活')
    else:
        return HttpResponse('激活失败！')

def user_auth_reset_password(request,raw_activation_key):
    """
    用于验证密码有效性并修改密码
    """
    user = User.objects.get(userauth__activation_key=raw_activation_key)
    is_valid = user.userauth.confirm_activation_key()
    if user and is_valid:
        if request.method == 'POST':
            form = Reset_Password_Form(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                user.set_password(password)
                user.userauth.activation_valid = False
                user.save()
                return render(request,'user_auth/reset_password_complete.html',{})
        else:
            form = Reset_Password_Form()

        return render(request,'user_auth/reset_password.html',{'form':form})
    else:
        return Http404('页面不存在')