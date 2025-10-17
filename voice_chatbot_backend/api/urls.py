from django.urls import path
from .views import health, stt, chat, tts

urlpatterns = [
    path('health/', health, name='Health'),
    path('stt/', stt, name='STT'),
    path('chat/', chat, name='Chat'),
    path('tts/', tts, name='TTS'),
]
