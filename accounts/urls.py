from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
]
