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
import requests,math,random,boto3
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
        bmi = float(request.POST['bmi'])
        UserProfile(user=request.user,full_name=full_name,gender=gender,weight=weight,height=height,bmi=bmi).save()
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
        profile.bmi = float(request.POST['bmi'])
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
    return render(request, 'exercises/view_exercises.html',{'exercises':exercises})

@login_required(login_url='user_login')
def search_exercises(request):
    if request.method=="POST":
        exercise_name = request.POST['exercise_name']
        exercise = Exercise.objects.filter(exercise_name=exercise_name).first()
        return render(request,'user_app/search_exercises.html',{'exercise':exercise})

@login_required(login_url='user_login')
def view_progress(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    progress = UserProgress.objects.filter(profile=profile).all().order_by('-date_time')
    return render(request,'user_app/view_progress.html',{'progress':progress})

@login_required(login_url='user_login')
def start_exercise(request,uid):
    exercise = Exercise.objects.filter(uid=uid).first()
    poses = Pose.objects.filter(exercise=exercise).all()
    threshold = []
    for i in range(0,11):
        threshold[i] = (pose[0][i]+pose[1][i])/2
    avg_threshold = sum(threshold)/len(threshold)
    request.session['threshold'] = threshold
    request.session['avg_threshold'] = avg_threshold
    request.session['stage'] = "None"
    request.session['reps'] = 0
    request.session['user_max_angles']=[]
    request.session['user_min_angles']=[]
    request.session['total_reps'] = exercise.reps


    return render(request,'user_app/start_exercise.html',{'exercise':exercise})

@csrf_exempt(login_url='user_login')
def score_user(request,uid):
    cur_angles = request.GET.get('cur_angles')
    cur_avg = sum(cur_angles)/len(cur_angles)
    if cur_avg > request.session['avg_threshold']:
        if request.session['stage']=="min":
            request.session['reps'] += 0.5
        request.session['stage'] = "max"
        if request.session['user_max_angles'][int(request.session['reps'])] is None:
            request.session['user_max_angles'][int(request.session['reps'])] = cur_angles.copy()
        else:
            if cur_avg > sum(request.session['user_max_angles'][int(request.session['reps'])])/len(request.session['user_max_angles'][int(request.session['reps'])]):
                request.session['user_max_angles'][int(request.session['reps'])]=cur_angles.copy()
    if cur_avg < request.session['avg_threshold']:
        if request.session['stage']=="max":
            request.session['reps'] += 0.5
        request.session['stage'] = "min"
        if request.session['user_min_angles'][int(request.session['reps'])] is None:
            request.session['user_min_angles'][int(request.session['reps'])] = cur_angles.copy()
        else:
            if cur_avg < sum(request.session['user_min_angles'][int(request.session['reps'])])/len(request.session['user_min_angles'][int(request.session['reps'])]):
                request.session['user_min_angles'][int(request.session['reps'])]=cur_angles.copy()
    if request.session['reps']==request.session['total_reps']:
        max_diff = 0
        min_diff=0
        exercise = Exercise.objects.filter(uid=uid).first()
        poses = Pose.objects.filter(exercise=exercise).all()
        for rep in request.session['total_reps']:
            max_diff += ((sum(request.session['user_max_angles'][rep]-poses[0])/12)/request.session['avg_threshold'])*100
            min_diff += ((sum(request.session['user_min_angles'][rep]-poses[0])/12)/request.session['avg_threshold'])*100
        max_diff /= exercise.reps
        min_diff /= exercise.reps
        score = 100-max_diff-min_diff
        print(score)
        UserProgress(exercise=exercise,profile = UserProfile.objects.filter(user=request.user).first(),points_earned=score).save()
        return JsonResponse({'redirect_url':'/user_app/view_progress/'})
        



