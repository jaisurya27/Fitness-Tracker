from django.shortcuts import render,redirect
from django.contrib import auth
from django.http import JsonResponse,HttpResponse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests,math,random,boto3
from accounts.models import *
from app.models import *
import cv2
import mediapipe as mp
import numpy as np
UserModel = get_user_model()

mp_pose = mp.solutions.pose
angles = [(23,11,13),(14,12,24),(11,13,15),(12,14,16),(13,15,19),(14,16,20),(11,23,25),(12,24,26),(23,25,27),(24,26,28),(25,27,31),(26,28,32)]

def calculate_angle(a,b,c):
    a = np.array(a) 
    b = np.array(b) 
    c = np.array(c) 
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

@login_required(login_url='admin_login')
def add_exercise(request):
    if request.method=="POST":
        reps = duration = None
        exercise_name = request.POST['exercise_name']
        exercise_description = request.POST['exercise_description']
        if "duration" in request.POST:
            duration = request.POST['duration']
        else:
            reps = request.POST['reps']
        video = request.FILES['video']
        exercise = Exercise(added_by=request.user, exercise_name=exercise_name, exercise_description=exercise_description, duration = duration, reps = reps, video=video )
        exercise.save()
        cap = cv2.VideoCapture(exercise.video)
        max_angle = []
        min_angle = []
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                results = pose.process(frame)
                try:
                    curr_angles = []
                    landmark = results.pose_landmarks.landmark
                    for ang in angles:
                        curr_angles.append(calculate_angle([landmark[ang[0]].x,landmark[ang[0]].y],[landmark[ang[1]].x,landmark[ang[1]].y],[landmark[ang[2]].x,landmark[ang[2]].y]))
                    if len(max_angle)==0:
                        max_angle = curr_angles.copy()
                    else:
                        avg_curr = sum(curr_angles)/len(curr_angles)
                        avg_max = sum(max_angle)/len(max_angle)
                        if avg_curr > avg_max:
                            max_angle = curr_angles.copy()
                    if len(min_angle)==0:
                        min_angle = curr_angles.copy()
                    else:
                        avg_curr = sum(curr_angles)/len(curr_angles)
                        avg_min = sum(min_angle)/len(min_angle)
                        if avg_curr < avg_min:
                            min_angle = curr_angles.copy()
                except:
                    pass
                
                if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    break
            cap.release()
            cv2.destroyAllWindows()
            Pose(exercise=exercise,left_shoulder=max_angle[0],right_shoulder=max_angle[1],left_elbow=max_angle[2],right_elbow=max_angle[3],left_wrist=max_angle[4],right_wrist=max_angle[5],left_hip=max_angle[6],right_hip=max_angle[7],left_knee=max_angle[8],right_knee=max_angle[9],left_ankle=max_angle[10],right_ankle=max_angle[11]).save()
            Pose(exercise=exercise,left_shoulder=min_angle[0],right_shoulder=min_angle[1],left_elbow=min_angle[2],right_elbow=min_angle[3],left_wrist=min_angle[4],right_wrist=min_angle[5],left_hip=min_angle[6],right_hip=min_angle[7],left_knee=min_angle[8],right_knee=min_angle[9],left_ankle=min_angle[10],right_ankle=min_angle[11]).save()

        return redirect('admin_view_exercise')
    else:
        return render(request,'admin_app/add_exercise.html')

@login_required(login_url='admin_login')
def view_exercise(request):
    exercises = Exercise.objects.filter(added_by = request.user).all()
    return render(request,'admin_app/view_exercise.html',{"exercises":exercises})

