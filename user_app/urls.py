from django.urls import path
from . import views

urlpatterns = [
    path('view_profile/',views.view_profile,name='view_profile'),
    path('add_profile/',views.add_profile,name='add_profile'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('view_exercises/',views.view_exercises,name='view_exercises'),
    path('score_user/',views.score_user,name='score_user'),
    path('view_progress/',views.view_progress,name='view_progress'),
]