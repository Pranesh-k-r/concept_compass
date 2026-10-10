from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('subjects/', views.subject_selection, name='subject_selection'),
    path('start/', views.start_quiz, name='start_quiz'),
    path('<int:session_id>/question/', views.quiz_question, name='quiz_question'),
    path('<int:session_id>/report/', views.diagnostic_report, name='diagnostic_report'),
]
