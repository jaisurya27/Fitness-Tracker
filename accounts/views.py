from django.shortcuts import render,redirect
from django.contrib import auth
from django.http import JsonResponse,HttpResponse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib import messages
from .admin import UserCreationForm
import requests,math,random
from .models import *
UserModel = get_user_model()

def home(request):
    return render(request,'accounts/index.html')

def admin_signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = User(email=email,is_admin=True)
        user.set_password(password)
        user.save()
        auth.login(request,user,backend=None)
        return redirect('admin_view_exercise')
    else:
        return render(request,'accounts/admin_signup.html')

def admin_login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(username=email,password=password)
        if user is not None:
            auth.login(request,user,backend=None)
            return redirect('admin_view_exercise')
        else:
            return redirect('admin_login')
    else:
        return render(request,'accounts/admin_login.html')

def user_signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = User(email=email)
        user.set_password(password)
        user.save()
        auth.login(request,user,backend=None)
        return redirect('add_profile')
    else:
        return render(request,'accounts/user_signup.html')

def user_login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(username=email,password=password)
        if user is not None:
            auth.login(request,user,backend=None)
            return redirect('view_profile')
        else:
            return redirect('user_login')
    else:
        return render(request,'accounts/user_login.html')

def logout(request):
    auth.logout(request)
    return redirect('home')