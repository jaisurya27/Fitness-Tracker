from django.shortcuts import render,redirect
from django.contrib import auth
from django.http import JsonResponse,HttpResponse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from accounts.models import *
from .models import *
import cv2
import mediapipe as mp
import numpy as np
import pymongo

UserModel = get_user_model()

angles = [(23,11,13),(14,12,24),(11,13,15),(12,14,16),(13,15,19),(14,16,20),(11,23,25),(12,24,26),(23,25,27),(24,26,28),(25,27,31),(26,28,32)]

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

def omit(exercise_type,omitted_angles):
    if exercise_type == "upper_body":
        for i in [8,9,10,11]:
            if i not in omitted_angles:
                omitted_angles.append(i)
    elif exercise_type == "lower_body":
        for i in [0,1,2,3,4,5]:
            if i not in omitted_angles:
                omitted_angles.append(i)
    omitted_angles.sort()

@login_required(login_url='admin_login')
def add_exercise(request):
    if request.method=="POST":
        exercise_name = request.POST['exercise_name']
        exercise_description = request.POST['exercise_description']
        exercise_category = request.POST['exercise_category']
        exercise_type = request.POST['exercise_type']
        duration = int(request.POST['duration'])
        reps = int(request.POST['reps'])
        video = request.FILES['video']
        exercise = Exercise(added_by=request.user, exercise_name=exercise_name, exercise_description=exercise_description,exercise_category = exercise_category, exercise_type=exercise_type, duration = duration, reps = reps, video=video )
        exercise.save()
        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture("uploads/"+str(exercise.video))
        if exercise_category == "single_pose":
            avg_angles = []
            avg_visib = []
            avg_z=[]
            omitted_angles =[]
            c=0
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    ret, frame = cap.read()
                    results = pose.process(frame)
                    try:
                        curr_angles = []
                        curr_visib = []
                        curr_z=[]
                        landmark = results.pose_landmarks.landmark
                        for ang in angles:
                            curr_visib.append(landmark[ang[1]].visibility)
                            curr_angles.append(calculate_angle([landmark[ang[0]].x,landmark[ang[0]].y],[landmark[ang[1]].x,landmark[ang[1]].y],[landmark[ang[2]].x,landmark[ang[2]].y]))
                            curr_z.append(landmark[ang[1]].z)
                        if len(avg_angles)==0:
                            avg_angles=curr_angles.copy()
                            avg_visib=curr_visib.copy()
                            avg_z = curr_z.copy()
                        else:
                            for i in range(0,12):
                                avg_angles[i] += curr_angles[i]
                                avg_visib[i]+= curr_visib[i]
                                avg_z[i]+= curr_z[i]
                        c=c+1
                    except:
                        pass
                    
                    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                        break
                cap.release()
                cv2.destroyAllWindows()

            avg_angles = [i/c for i in avg_angles].copy()
            avg_visib = [i/c for i in avg_visib].copy()
            avg_z = [i/c for i in avg_z].copy()

            for i in range(0,len(avg_visib)):
                if avg_visib[i]<0.5:
                    omitted_angles.append(i)
            omit(exercise_type,omitted_angles)
            client = pymongo.MongoClient("mongodb://localhost:27017/")
            db = client["ssg"]
            col = db["pose"]

            pose = {"ref_angles":avg_angles,"ref_visibility":avg_visib,"ref_z_coords":avg_z,"omitted_angles":omitted_angles}

            p = col.insert_one(pose)
            Pose(exercise = exercise,pose_id = p.inserted_id).save()
        else:
            max_angle = []
            min_angle = []
            max_visib=[]
            min_visib=[]
            max_z = []
            min_z = []
            omitted_angles = []
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    ret, frame = cap.read()
                    results = pose.process(frame)
                    try:
                        curr_angles = []
                        curr_visib=[]
                        curr_z=[]
                        landmark = results.pose_landmarks.landmark
                        for ang in angles:
                            curr_z.append(landmark[ang[1]].z)
                            curr_visib.append(landmark[ang[1]].visibility)
                            curr_angles.append(calculate_angle([landmark[ang[0]].x,landmark[ang[0]].y],[landmark[ang[1]].x,landmark[ang[1]].y],[landmark[ang[2]].x,landmark[ang[2]].y]))
                        if len(max_angle)==0:
                            max_angle = curr_angles.copy()
                            max_visib = curr_visib.copy()
                            max_z = curr_z.copy()
                        else:
                            avg_curr = sum(curr_angles)/len(curr_angles)
                            avg_max = sum(max_angle)/len(max_angle)
                            if avg_curr > avg_max:
                                max_angle = curr_angles.copy()
                                max_visib = curr_visib.copy()
                                max_z = curr_z.copy()
                        if len(min_angle)==0:
                            min_angle = curr_angles.copy()
                            min_visib = curr_visib.copy()
                            min_z = curr_z.copy()
                        else:
                            avg_curr = sum(curr_angles)/len(curr_angles)
                            avg_min = sum(min_angle)/len(min_angle)
                            if avg_curr < avg_min:
                                min_angle = curr_angles.copy()
                                min_visib = curr_visib.copy()
                                min_z = curr_z.copy()
                    except:
                        pass
                    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                        break
                cap.release()
                cv2.destroyAllWindows()
            for i in range(0,12):
                if max_visib[i]<0.5 or min_visib[i]<0.5:
                    omitted_angles.append(i)
            omit(exercise_type,omitted_angles)
            client = pymongo.MongoClient("mongodb://localhost:27017/")
            db = client["ssg"]
            col = db["pose"]

            pose = {"ref_max_angles":max_angle,"ref_max_visibility":max_visib,"ref_max_z_coords":max_z,"ref_min_angles":min_angle,"ref_min_visibility":min_visib,"ref_min_z_coords":min_z,"omitted_angles":omitted_angles}

            p = col.insert_one(pose)
            Pose(exercise = exercise,pose_id = p.inserted_id).save()
        return redirect('admin_view_exercise')
    else:
        return render(request,'admin_app/add_exercise.html')

@login_required(login_url='admin_login')
def view_exercise(request):
    exercises = Exercise.objects.filter(added_by = request.user).all()
    return render(request,'admin_app/view_exercise.html',{"exercises":exercises})

@csrf_exempt
def return_pose(request):
    exercise_id = request.GET.get('exercise_id')
    exercise = Exercise.objects.filter(uid = exercise_id).first()
    pose = Pose.objects.filter(exercise = exercise).first()
    return JsonResponse({'pose_id':pose.pose_id,'duration':exercise.duration,'reps':exercise.reps})

