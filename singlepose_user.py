import cv2
import mediapipe as mp
import numpy as np
import time
import requests
import pymongo
from bson.objectid import ObjectId 

exercise_id = '1a21f893-cc73-4175-8b90-6d4003a4af6f'
user_id = 3
pose = requests.get('http://127.0.0.1:8000/admin_app/return_pose/',{'exercise_id':exercise_id,'user_id':user_id}).json()
pose_id = pose['pose_id']
duration = pose['duration']

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ssg"]
col = db["pose"]

   
data = col.find_one({'_id': ObjectId(str(pose_id))})




#returned from the reference:
ref_angles = data['ref_angles']
omitted_angles = data['omitted_angles']

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
angles = [(23,11,13),(14,12,24),(11,13,15),(12,14,16),(13,15,19),(14,16,20),(11,23,25),(12,24,26),(23,25,27),(24,26,28),(25,27,31),(26,28,32)]
cap = cv2.VideoCapture(0)
angle_diff=[]
avg_visib=[]
c=0
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    start = time.time()
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
            curr_visib = []
            landmark = results.pose_landmarks.landmark

            for ang in angles:
                curr_angles.append(calculate_angle([landmark[ang[0]].x,landmark[ang[0]].y],[landmark[ang[1]].x,landmark[ang[1]].y],[landmark[ang[2]].x,landmark[ang[2]].y]))
                curr_visib.append(landmark[ang[1]].visibility)
            if len(angle_diff)==0:
                for i in range(0,12):
                    angle_diff.append(abs(ref_angles[i]-curr_angles[i])) 
                avg_visib=curr_visib.copy()
            else:
                for i in range(0,12):
                    angle_diff[i] += abs(ref_angles[i]-curr_angles[i])
                    avg_visib[i]+= curr_visib[i]
            c=c+1
        except:
            pass
        if time.time()-start >= duration:
            break
    cap.release()
    cv2.destroyAllWindows()
print(c)
angle_diff = [i/c for i in angle_diff].copy()
avg_visib = [i/c for i in avg_visib].copy()

for i in range(0,len(angle_diff)):
    if avg_visib[i]<0.5:
        angle_diff[i]=100

t=0
for i in omitted_angles:
    del angle_diff[i-t]
    t+=1

avg_angle_diff = sum(angle_diff)/len(angle_diff)

score = None
if avg_angle_diff>40:
    score=0         #Workout is not done
elif avg_angle_diff<40 and avg_angle_diff>15:
    score = (40-avg_angle_diff) * 3.6
else:
    score = (15-avg_angle_diff) * 0.67
    score = score + 90


print("score:", score)

requests.get('http://127.0.0.1:8000/user_app/score_user/',{'exercise_id':exercise_id,'user_id':user_id,'score':score})





