from django.urls import path
from .views import message_list, get_messages

urlpatterns = [
    path('emails/', message_list, name='message_list'),
    path('messages/', get_messages),
]

