from django.db import models
import django
# Create your models here.
from accounts.models import *
from admin_app.models import *

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    full_name = models.TextField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    height = models.IntegerField()
    weight = models.IntegerField()
    bmi = models.FloatField()

class UserProgress(models.Model):
    exercise = models.ForeignKey(Exercise,on_delete=models.SET_NULL, null=True)
    profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    points_earned = models.FloatField()
    date_time = models.DateTimeField(default = django.utils.timezone.now)