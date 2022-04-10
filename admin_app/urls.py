from django.urls import path
from . import views

urlpatterns = [
    path('view_exercise/',views.view_exercise,name='admin_view_exercise'),
    path('add_exercise/',views.add_exercise,name='add_exercise'),
]