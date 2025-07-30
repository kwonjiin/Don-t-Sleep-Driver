import cv2, dlib, numpy as np
from scipy.spatial import distance as dist
from datetime import datetime
from audio import play_alarm, stop_alarm, speak_warning
from logger import log_event

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

EAR_DROP_RATIO = 0.7
YAWN_RATIO = 1.5
HEAD_TILT_RATIO = 1.3
FRAME_THRESHOLD = 20

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def drowsiness_detection(stop_event, on_end_callback):
    initial_ear, initial_mouth_height, initial_head_tilt = None, None, None
    drowsy_frames = 0
    drowsy_count = 0
    last_drowsy_state = 0
    session_start = datetime.now()

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        if stop_event.is_set():
            break

        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)
            points = np.array([[p.x, p.y] for p in landmarks.parts()])

            left_eye, right_eye = points[36:42], points[42:48]
            mouth = points[48:68]

            ear = (eye_aspect_ratio(left_eye)+eye_aspect_ratio(right_eye))/2.0
            mouth_height = dist.euclidean(mouth[3], mouth[9])
            head_tilt = abs(points[27][1] - points[8][1]) / face.height()

            # 초기값 저장
            if initial_ear is None: initial_ear = ear
            if initial_mouth_height is None: initial_mouth_height = mouth_height
            if initial_head_tilt is None: initial_head_tilt = head_tilt

            # 트리형 로직
            drowsy_state = 0
            if ear < initial_ear * EAR_DROP_RATIO:
                drowsy_state = 1
                if mouth_height > initial_mouth_height * YAWN_RATIO:
                    drowsy_state = 2
                    if head_tilt > initial_head_tilt * HEAD_TILT_RATIO:
                        drowsy_state = 3

            # 프레임 카운트
            drowsy_frames = drowsy_frames + 1 if drowsy_state >= 2 else max(0, drowsy_frames -1)

            # 알람 처리
            if drowsy_frames >= FRAME_THRESHOLD:
                if drowsy_state == 2:
                    play_alarm()
                elif drowsy_state ==3:
                    play_alarm()
                    speak_warning()
            else:
                stop_alarm()

            # 졸음 이벤트 카운트
            if drowsy_state >= 2 and last_drowsy_state < 2:
                drowsy_count += 1
            last_drowsy_state = drowsy_state

            # 로그 저장
            log_event(ear, mouth_height, head_tilt, drowsy_state)

        cv2.imshow("Drowsiness Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    on_end_callback(session_start, drowsy_count)