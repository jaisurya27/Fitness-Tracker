import cv2
import mediapipe as mp
import numpy as np
import requests
import pymongo
from bson.objectid import ObjectId 

exercise_id = '2b706d4d-eb44-4b6a-a686-b5b858fcfb66'
user_id = 3
pose = requests.get('http://127.0.0.1:8000/admin_app/return_pose/',{'exercise_id':exercise_id,'user_id':user_id}).json()
pose_id = pose['pose_id']
reps = pose['reps']

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ssg"]
col = db["pose"]
   
data = col.find_one({'_id': ObjectId(str(pose_id))})

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

ref_max_angles = data['ref_max_angles']
ref_min_angles = data['ref_min_angles']
omitted_angles = data['omitted_angles']

t=0
for i in omitted_angles:
    del ref_max_angles[i-t]
    del ref_min_angles[i-t]
    t+=1

threshold = []
for i in range(0,len(ref_max_angles)):
    threshold.append((ref_max_angles[i]+ref_min_angles[i])/2)
 
avg_threshold = sum(threshold)/len(threshold)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
angles = [(23,11,13),(14,12,24),(11,13,15),(12,14,16),(13,15,19),(14,16,20),(11,23,25),(12,24,26),(23,25,27),(24,26,28),(25,27,31),(26,28,32)]
cap = cv2.VideoCapture(0)
state = "max"
rep = 0
max_avg = 0
min_avg = 0
max_angle = []
min_angle = []
count = 0
initial_state = 0
total_score = 0
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                 ) 
        cv2.imshow('Mediapipe Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        try:
            curr_angles = []
            landmark = results.pose_landmarks.landmark
            for ang in angles:
                curr_angles.append(calculate_angle([landmark[ang[0]].x,landmark[ang[0]].y],[landmark[ang[1]].x,landmark[ang[1]].y],[landmark[ang[2]].x,landmark[ang[2]].y]))
            t=0
            for i in omitted_angles:
                del curr_angles[i-t]
                t+=1
            avg_curr_angles = sum(curr_angles)/len(curr_angles)

            if state == "min" and avg_curr_angles > avg_threshold:
                if initial_state==3:
                    count+=1
                if count == 4:
                    rep += 1
                    state = "max"
                    #score:
                    
                    min_angle_diff = []
                    for i in range(0,len(ref_min_angles)):
                        min_angle_diff.append(abs(ref_min_angles[i]-min_angle[i]))
                    avg_min_angle_diff = sum(min_angle_diff)/len(min_angle_diff)
                                
                    if avg_min_angle_diff>40:
                        min_score=0         #Workout is not done
                    elif avg_min_angle_diff<=40 and avg_min_angle_diff>15:
                        min_score = (40-avg_min_angle_diff) * 3.66
                    else:
                        min_score = (15-avg_min_angle_diff) * 0.67
                        min_score = min_score + 90

                    print(rep," : ",(max_score+min_score)/2)
                    total_score += (max_score+min_score)/2
                    if rep==reps:
                        cap.release()
                        cv2.destroyAllWindows()   
                    max_angle = curr_angles.copy()
                    max_avg = avg_curr_angles
                    initial_state = 1
                    count=0
                else:
                    pass
                    
            elif state == "max" and avg_curr_angles >avg_threshold:
                if initial_state==0 or initial_state==1:
                    count +=1
                    initial_state =2
                if max_avg==0 and len(max_angle)==0:
                    max_avg=avg_curr_angles
                    max_angle = curr_angles.copy()
                elif avg_curr_angles > max_avg:
                    max_avg = avg_curr_angles
                    max_angle = curr_angles.copy()
            elif state == "min" and avg_curr_angles < avg_threshold:
                if initial_state == 4:
                    count +=1
                    initial_state =3
                if avg_curr_angles < min_avg:
                    min_avg = avg_curr_angles
                    min_angle = curr_angles.copy()
            elif state=="max" and avg_curr_angles < avg_threshold:
                if initial_state==2:
                    count +=1
                if count==2:
                    initial_state=4
                    state = "min"

                    max_angle_diff = []
                    for i in range(0,len(ref_max_angles)):
                        max_angle_diff.append(abs(ref_max_angles[i]-max_angle[i]))
                    avg_max_angle_diff = sum(max_angle_diff)/len(max_angle_diff)
                    if avg_max_angle_diff>40:
                        max_score=0         #Workout is not done
                    elif avg_max_angle_diff<=40 and avg_max_angle_diff>15:
                        max_score = (40-avg_max_angle_diff) * 3.66
                    else:
                        max_score = (15-avg_max_angle_diff) * 0.67
                        max_score = max_score + 90
                        
                    min_angle = curr_angles.copy()
                    min_avg = avg_curr_angles
                
        except Exception as e:
            print(e)
    cap.release()
    cv2.destroyAllWindows()

total_score /= rep
requests.get('http://127.0.0.1:8000/user_app/score_user/',{'exercise_id':exercise_id,'user_id':user_id,'score':total_score})



