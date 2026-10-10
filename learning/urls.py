from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('lesson/<str:concept_id>/', views.targeted_lesson, name='lesson'),
    path('practice/<str:concept_id>/', views.practice, name='practice'),
    path('verify/<str:concept_id>/', views.verify, name='verify'),
    path('api/solve/', views.api_solve_problem, name='api_solve_problem'),
]
