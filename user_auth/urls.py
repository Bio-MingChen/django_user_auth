from django.urls import re_path,path
from . import views

app_name = 'user_auth'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/',views.login_page, name='login'),
    path('logout/',views.logout_page,name='logout'),
    path('registration/',views.user_auth_registration,name='registration'),
    path('registration/resend_email/<username>/<email>/',views.resend_activation_email,
        name='registration_resend_email'),
    re_path(r'registration/activation/(?P<raw_activation_key>[\w-]+)/$',views.user_auth_activation,
        name='registration_activation'),
    path('reset_password/send_email/',views.user_auth_send_email,name='password_send_email'),
    re_path(r'reset_password/activation/(?P<raw_activation_key>[\w-]+)/$',views.user_auth_reset_password,
        name='reset_password'),
]