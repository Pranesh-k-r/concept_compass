from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.chat_interface, name='chat'),
    path('api/message/', views.send_message, name='send_message'),
    path('explain-mistake/', views.explain_mistake, name='explain_mistake'),
    path('find-gap/', views.find_gap, name='find_gap'),
    path('practice-with-me/', views.practice_mode, name='practice_mode'),
]
