from django.db import models
from accounts.models import *
import uuid

class Exercise(models.Model):
    added_by = models.ForeignKey(User,on_delete=models.CASCADE)
    uid = models.UUIDField(default = uuid.uuid4,editable = False)
    exercise_name = models.TextField()
    exercise_description = models.TextField()
    duration = models.FloatField(default=0)
    reps = models.IntegerField(default=0)
    video = models.FileField(upload_to='video/')

class Pose(models.Model):
    exercise = models.ForeignKey(Exercise,on_delete=models.CASCADE)
    left_shoulder = models.Floatfield()
    right_shoulder = models.Floatfield() 
    left_elbow = models.Floatfield() 
    right_elbow = models.Floatfield()
    left_wrist = models.Floatfield()
    right_wrist = models.Floatfield() 
    left_hip = models.Floatfield() 
    right_hip = models.Floatfield()
    left_knee = models.Floatfield()
    right_knee = models.Floatfield() 
    left_ankle = models.Floatfield() 
    right_ankle = models.Floatfield()  