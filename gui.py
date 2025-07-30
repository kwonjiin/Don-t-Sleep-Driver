import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from logger import summarize_session
from detector import drowsiness_detection

stop_event = Event()  # 감지 종료를 위한 이벤트
detection_thread = None

def start_detection():
    global detection_thread
    stop_event.clear()  # 감지 시작 전 stop 이벤트 초기화
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    detection_thread = Thread(
        target=drowsiness_detection, 
        args=(stop_event, on_detection_end)
        )
    detection_thread.start()

def stop_detection():
    global detection_thread
    stop_event.set()  # 감지 중단 요청
    stop_button.config(state="disabled")  # 즉시 버튼 비활성화
    if detection_thread and detection_thread.is_alive():
        detection_thread.join(timeout=1)

def on_detection_end(start_time, drowsy_count):
    session_info = summarize_session(start_time, drowsy_count)
    messagebox.showinfo("운전 세션 요약", session_info)
    start_button.config(state="normal")
    stop_button.config(state="disabled")

def on_close():
    stop_detection()
    root.destroy()

root = tk.Tk()
root.title("Don't Sleep Driver")
root.geometry("400x300")

label = tk.Label(root, text="Don't Sleep Driver", font=("Arial", 24))
label.pack(pady=50)

start_button = tk.Button(root, text="시작", font=("Arial", 16), command=start_detection)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="종료", font=("Arial", 16), state="disabled", command=stop_detection)
stop_button.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()