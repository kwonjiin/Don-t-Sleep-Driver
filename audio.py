import pygame 
from gtts import gTTS
import os

pygame.mixer.init()
pygame.mixer.music.load("alarm.mp3")

def play_alarm():
    """기본 알람음 재생"""
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

def stop_alarm():
    """알람 정지"""
    pygame.mixer.music.stop()

def speak_warning():
    """TTS 음성 경고"""
    tts = gTTS("졸음 운전 감지! 휴식을 취하세요.", lang='ko')
    tts.save("warning.mp3")
    os.system("start warning.mp3")