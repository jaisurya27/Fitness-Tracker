import numpy as np
from math import sqrt
from django.shortcuts import render,redirect
from django.contrib import auth
from django.http import JsonResponse,HttpResponse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from accounts.models import *
from .models import *
from accounts.models import *
from admin_app.models import *
UserModel = get_user_model()

@login_required(login_url='user_login')
def add_profile(request):
    if request.method=="POST":
        full_name = request.POST['full_name']
        age = int(request.POST['age'])
        gender = request.POST['gender']
        height = int(request.POST['height'])
        weight = int(request.POST['weight'])
        bmi = (weight/(height*height)) * 10000
        UserProfile(user=request.user,full_name=full_name,age=age,gender=gender,weight=weight,height=height,bmi=bmi).save()
        return redirect('view_profile')
    else:
        return render(request,'user_app/add_profile.html')

@login_required(login_url='user_login')
def edit_profile(request):
    if request.method=="POST":
        profile = UserProfile.objects.filter(user=request.user).first()
        profile.full_name = request.POST['full_name']
        profile.age = int(request.POST['age'])
        profile.gender = request.POST['gender']
        profile.height = int(request.POST['height'])
        profile.weight = int(request.POST['weight'])
        profile.bmi = (profile.weight/(profile.height*profile.height)) * 10000
        profile.save()
        return redirect('view_profile')
    else:
        profile = UserProfile.objects.filter(user=request.user).first()
        return render(request,'user_app/edit_profile.html',{'profile':profile})

@login_required(login_url='user_login')
def view_profile(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    return render(request,'user_app/view_profile.html',{'profile':profile})

@login_required(login_url='user_login')
def view_exercises(request):
    exercises = Exercise.objects.all().order_by('exercise_name')
    return render(request, 'user_app/view_exercises.html',{'exercises':exercises})

@login_required(login_url='user_login')
def view_progress(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    progress = UserProgress.objects.filter(profile=profile).all().order_by('-date_time')
    return render(request,'user_app/view_progress.html',{'progress':progress})

@csrf_exempt
def score_user(request):
    exercise_id = request.GET.get('exercise_id')
    user_id = request.GET.get('user_id')
    user = User.objects.filter(pk = user_id).first()
    profile = UserProfile.objects.filter(user = user).first()
    exercise = Exercise.objects.filter(uid = exercise_id).first()
    score = request.GET.get('score')
    UserProgress(exercise=exercise, profile= profile, points_earned=score).save()
    return JsonResponse({'is_added':True})




