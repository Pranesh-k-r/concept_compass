from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('history/', views.history, name='history'),
    path('graph/', views.concept_graph, name='graph'),
    path('study-plan/', views.study_plan, name='study_plan'),
    path('study-plan/complete/<int:task_id>/', views.mark_task_complete, name='mark_task_complete'),
]
