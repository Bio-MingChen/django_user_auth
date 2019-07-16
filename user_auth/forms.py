from django import forms
from django.contrib.auth.models import User

class Login_Form(forms.Form):

    username = forms.CharField(label="用户名",widget=forms.TextInput(),max_length=64)
    password = forms.CharField(label='登陆密码',widget=forms.PasswordInput(),max_length=64)


class Send_Email_Form(forms.Form):

    email = forms.EmailField(label='邮箱',help_text=
    '请输入你的邮箱地址')

    def clean_email(self):
        """
        确认是否存在该邮箱
        """
        if not User.objects.filter(email=self.cleaned_data['email']):
            raise forms.ValidationError('该邮箱还未注册过，请检查!',code='invalid_email')
        return self.cleaned_data['email']

class Registration_Form(forms.ModelForm):

    username = forms.CharField(max_length=64,label='用户名',
        widget=forms.TextInput(attrs={'placeholder':'用户名'}),
        # error_messages={'required':'不能为空','max_length':'要求64个字符以内'}
        )
    confirm_password = forms.CharField(label='重新输入密码',max_length=64,widget=forms.PasswordInput(attrs={'class':'form-control',
    'placeholder':'重复输入密码',
    }))
    password = forms.CharField(label='登陆密码',max_length=64,widget=forms.PasswordInput(attrs={'class':'form-control',
    'placeholder':'登陆密码',
    }))
    email = forms.EmailField(label='用户邮箱',widget=forms.EmailInput(attrs={'placeholder':'用户邮箱'}))
    
    class Meta:
        model = User
        fields = ['username','password','confirm_password','email'] #添加confirm_password以调整顺序

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError('两次密码输入不一致，请检查！',code='password error')
           
        return self.cleaned_data

    def clean_email(self): #函数名是严格限制的 clean+下划线+字段
        """
        用于验证邮箱的唯一性
        """
        if User.objects.filter(email__exact=self.cleaned_data['email']):
            raise forms.ValidationError('该Email已经注册过了，请检查!',code='invalid email')
        return self.cleaned_data['email']

    
class Reset_Password_Form(forms.Form):
    """
    #这里特别需要注意的是参数的顺序，因为在clean_password中用到了confirm_password，因此
    #需要cleaned_data中事先已经存在confirm_password，为此，需要先通过confirm_password的
    #is_valid()，注意是有括号的，该函数将过滤没有问题的值添加到cleaned_data中，因此需要先
    #创建confirm_password然后再创建password
    """
    confirm_password = forms.CharField(widget=forms.PasswordInput,label='密码验证',max_length=64)
    password = forms.CharField(widget=forms.PasswordInput(),label='重置密码',max_length=64)
    
    def clean_password(self):
        if self.cleaned_data.get('confirm_password'):
            if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
                raise forms.ValidationError('密码两次输入不一致，请检查',code='password error')
        else:
            raise forms.ValidationError('输入有误，请检查')
        return self.cleaned_data['password']
