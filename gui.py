import tkinter as tk
from tkinter import messagebox
from opencv import drowsiness_detection
from threading import Thread

# 졸음 감지 시스템 시작
def start_detection():
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    
    # 별도의 쓰레드로 졸음 감지 시스템 실행
    detection_thread = Thread(target=drowsiness_detection, args=(on_detection_end,))
    detection_thread.start()

# 졸음 감지 종료 후 처리
def on_detection_end():
    start_button.config(state="normal")
    stop_button.config(state="disabled")
    messagebox.showinfo("알림", "졸음 운전 감지 시스템이 종료되었습니다.")

# GUI 설정
def stop_detection():
    # 종료 버튼 클릭 시 졸음 감지 시스템 종료
    pass

# GUI 창
root = tk.Tk()
root.title("Don't Sleep Driver")
root.geometry("400x300")

label = tk.Label(root, text="Don't Sleep Driver", font=("Arial", 24))
label.pack(pady=50)

start_button = tk.Button(root, text="시작", font=("Arial", 16), command=start_detection)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="종료", font=("Arial", 16), state="disabled", command=stop_detection)
stop_button.pack(pady=10)

root.mainloop()
