import csv
from datetime import datetime
import os

LOG_FILE = "logs/session_log.csv"

# Log 폴더 자동 생성
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_event(ear, mouth_height, head_tilt, drowsy_state):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now, 
            round(ear, 3), 
            round(mouth_height, 2), 
            round(head_tilt, 3), 
            drowsy_state
            ])
        
def summarize_session(start_time, drowsy_count):
    duration = datetime.now() - start_time
    minutes = int(duration.total_seconds() // 60)
    seconds = int(duration.total_seconds() % 60)
    return f"총 운전시간: {minutes}분 {seconds}초 \n 졸음 경고 발생 횟수: {drowsy_count}회"
