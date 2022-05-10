from django.db import models
from accounts.models import *
import uuid

class Exercise(models.Model):
    added_by = models.ForeignKey(User,on_delete=models.CASCADE)
    uid = models.UUIDField(default = uuid.uuid4,editable = False)
    exercise_name = models.TextField()
    exercise_description = models.TextField()
    exercise_category = models.CharField(max_length = 50, choices = [('single_pose','single_pose'),('multiple_pose','multiple_pose')])
    exercise_type = models.CharField(max_length = 50, choices = [('full_body','full_body'),('upper_body','upper_body'),('lower_body','lower_body')])
    duration = models.IntegerField(null = True)
    reps = models.IntegerField(null = True)
    video = models.FileField(upload_to='video/')

class Pose(models.Model):
    exercise = models.ForeignKey(Exercise,on_delete=models.CASCADE)
    pose_id = models.TextField()