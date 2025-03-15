import cv2
import dlib
import numpy as np
import pygame
from scipy.spatial import distance as dist
import threading

# # 초기화
pygame.mixer.init()
pygame.mixer.music.load("alarm.mp3")

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # 랜드마크 모델 필요

# 눈 감김 감지 함수
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# 비율 임계값 설정
EAR_THRESHOLD = 0.2
YAWN_THRESHOLD = 5
HEAD_TILT_THRESHOLD = 2
FRAME_THRESHOLD = 20


EAR_DROP_RATIO = 0.7  # 눈 크기가 초기 값의 70% 이하로 줄어들면 경고
FRAME_THRESHOLD = 20  # 경고 지속 프레임 수
drowsy_frames = 0
alert = False

initial_ear = None
initial_mouth_height = None
initial_head_tilt = None


# 졸음 감지 및 경고 시스템
def drowsiness_detection(callback):
    global initial_ear, initial_mouth_height, initial_head_tilt

    cap = cv2.VideoCapture(0)
    drowsy_frames = 0
    alert = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)
            points = np.array([[p.x, p.y] for p in landmarks.parts()])
            
            left_eye = points[36:42] if len(points) > 41 else []
            right_eye = points[42:48] if len(points) > 47 else []
            mouth = points[48:68] if len(points) > 67 else []
            
            ear = None
            mouth_height = None
            head_tilt = None


            # ear_left = eye_aspect_ratio(left_eye)
            # ear_right = eye_aspect_ratio(right_eye)
            # ear = (ear_left + ear_right) / 2.0
            
            # 눈감지 여부

            if len(left_eye) > 0 and len(right_eye) > 0:
                ear_left = eye_aspect_ratio(left_eye)
                ear_right = eye_aspect_ratio(right_eye)
                ear = (ear_left + ear_right) / 2.0


            # if left_eye is not None and right_eye is not None:
            #     ear_left = eye_aspect_ratio(left_eye)
            #     ear_right = eye_aspect_ratio(right_eye)
            #     ear = (ear_left + ear_right) / 2.0
            
            # 입 감지여부

            if len(mouth) > 0:
                mouth_height = dist.euclidean(mouth[3], mouth[9])
            # if mouth is not None:
            #     mouth_height = dist.euclidean(mouth[3], mouth[9])

            # 고개 기울기
            if len(points) > 8:
                head_tilt = abs(points[27][1] - points[8][1]) / face.height()

            # head_tilt = abs(points[27][1] - points[8][1]) / face.height()

            # mouth_height = dist.euclidean(mouth[3], mouth[9])
            

            # 초기 값 저장 (한 번만 실행됨)

            if initial_ear is None and ear is not None:
                initial_ear = ear
            if initial_mouth_height is None and mouth_height is not None:
                initial_mouth_height = mouth_height
            if initial_head_tilt is None and head_tilt is not None:
                initial_head_tilt = head_tilt

            # 얼굴 인식 셋중하나 안되면 이전상태 유지
            if ear is None and mouth_height is None:
                continue 

            # if initial_ear is None or initial_mouth_height is None or initial_head_tilt is None:
            #     initial_ear = ear
            #     initial_mouth_height = mouth_height
            #     initial_head_tilt = head_tilt
            #     print(f"초기 눈 EAR: {initial_ear}, 초기 입 크기: {initial_mouth_height}, 초기 고개 각도: {initial_head_tilt}")
            

            # 눈크기 절반, 입커짐(하품), 고개숙임시 경고
            conditions_met = sum([
                ear is not None and ear < initial_ear * EAR_DROP_RATIO,  
                mouth_height is not None and mouth_height> initial_mouth_height + YAWN_THRESHOLD,  
                head_tilt is not None and head_tilt > initial_head_tilt + HEAD_TILT_THRESHOLD  
            ])
            

            if conditions_met >= 1:
                drowsy_frames += 1
                alert = True
                pygame.mixer.music.play()
            else: 
                drowsy_frames = 0
                alert = False
                pygame.mixer.music.stop()
            
            # if drowsy_frames >= FRAME_THRESHOLD:
            #     alert = True
            #     pygame.mixer.music.play()
            
            if left_eye is not None:
                cv2.polylines(frame, [left_eye], isClosed=True, color=(0, 255, 0), thickness=2)
            
            if right_eye is not None:
                cv2.polylines(frame, [right_eye], isClosed=True, color=(0, 255, 0), thickness=2)
           
            if mouth is not None:
                cv2.polylines(frame, [mouth], isClosed=True, color=(0, 0, 255), thickness=2)
        
        if alert:
            overlay = frame.copy()
            overlay[:] = (0, 0, 255)  # 빨간색 레이어
            alpha = 0.5  # 투명도 50%
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        else:
            pass
        
        cv2.imshow("Drowsiness Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    # 콜백 호출 (GUI에서 알림을 받을 수 있도록)
    callback()

    print(ear)

    print(mouth_height)





# 쓰레딩한거

# 초기화
# pygame.mixer.init()
# pygame.mixer.music.load("alarm.mp3")

# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # 랜드마크 모델 필요

# # 눈 감김 감지 함수
# def eye_aspect_ratio(eye):
#     A = dist.euclidean(eye[1], eye[5])
#     B = dist.euclidean(eye[2], eye[4])
#     C = dist.euclidean(eye[0], eye[3])
#     return (A + B) / (2.0 * C)

# # 비율 임계값 설정
# EAR_THRESHOLD = 0.25
# YAWN_THRESHOLD = 30
# HEAD_TILT_THRESHOLD = 10
# FRAME_THRESHOLD = 20

# # 졸음 감지 및 경고 시스템
# def drowsiness_detection(callback):
#     cap = cv2.VideoCapture(0)
#     drowsy_frames = 0
#     alert = False

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = detector(gray)

#         for face in faces:
#             landmarks = predictor(gray, face)
#             points = np.array([[p.x, p.y] for p in landmarks.parts()])
            
#             left_eye = points[36:42]
#             right_eye = points[42:48]
#             mouth = points[48:68]
            
#             ear_left = eye_aspect_ratio(left_eye)
#             ear_right = eye_aspect_ratio(right_eye)
#             ear = (ear_left + ear_right) / 2.0
            
#             mouth_height = dist.euclidean(mouth[3], mouth[9])
#             head_tilt = abs(points[27][1] - points[8][1])
            
#             if ear < EAR_THRESHOLD or mouth_height > YAWN_THRESHOLD or head_tilt > HEAD_TILT_THRESHOLD:
#                 drowsy_frames += 1
#             else:
#                 drowsy_frames = 0
            
#             if drowsy_frames >= FRAME_THRESHOLD:
#                 alert = True
#                 pygame.mixer.music.play()
            
#             cv2.polylines(frame, [left_eye], isClosed=True, color=(0, 255, 0), thickness=2)
#             cv2.polylines(frame, [right_eye], isClosed=True, color=(0, 255, 0), thickness=2)
#             cv2.polylines(frame, [mouth], isClosed=True, color=(0, 0, 255), thickness=2)
        
#         if alert:
#             frame[:] = (0, 0, 255)  # 화면 빨갛게
        
#         cv2.imshow("Drowsiness Detection", frame)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

#     # 콜백 호출 (GUI에서 알림을 받을 수 있도록)
#     callback()

# # 쓰레드로 실행
# def start_detection():
#     detection_thread = threading.Thread(target=drowsiness_detection, args=(on_detection_end,))
#     detection_thread.start()

# # 콜백 함수 (졸음 감지 종료 후 호출)
# def on_detection_end():
#     print("졸음 감지 시스템 종료")
#     # 여기에 GUI에서 졸음 감지 종료 후 처리할 로직 추가

