from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('admin_signup/',views.admin_signup,name='admin_signup'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('user_signup/',views.user_signup,name='user_signup'),
    path('user_login/',views.user_login,name='user_login'),
    path('logout/',views.logout,name='logout')
]