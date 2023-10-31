import os
import time
import tkinter as tk
import threading
from datetime import datetime
from tkcalendar import DateEntry
from babel.numbers import format_decimal

file_name = "resign_date"

def init_select_frame(root):
    global cal, hour_input, minutes_input, start_button, stop_button
    
    current_date = datetime.now()
    
    select_frame = tk.Frame(root)
    cal = DateEntry(select_frame, 
            selectmode = 'day', 
            year = current_date.year, 
            month = current_date.month,
            day = current_date.day,
            width=30)
    time_label = tk.Label(select_frame, text="時間:")
    hour_input = tk.Entry(select_frame, width=5)
    split_label = tk.Label(select_frame, text=":")
    minutes_input = tk.Entry(select_frame, width=5)
    
    start_button = tk.Button(select_frame, text="開始倒數", width=12, command=set_target_date)
    stop_button = tk.Button(select_frame, text="停止倒數", width=12, command=stop_countdown, state=tk.DISABLED)
 
    select_frame.pack(pady=25)
    cal.grid(row=0, columnspan=5, padx=10, pady=10, sticky='w')
    time_label.grid(row=1, column=0, padx=10)
    hour_input.grid(row=1, column=1, padx=10)
    split_label.grid(row=1, column=2)
    minutes_input.grid(row=1, column=3, padx=10)
    start_button.grid(row=3,column=0,columnspan=2, padx=10)
    stop_button.grid(row=3,column=3,columnspan=2, padx=10)
    return select_frame

def init_countdown_frame(root):
    global target_time_label, countdown_label
    countdown_frame = tk.Frame(root)
    target_time_label = tk.Label(countdown_frame, text="X職時間:")
    countdown_label = tk.Label(countdown_frame, text="剩餘時間:")
    
    countdown_frame.pack()
    target_time_label.grid(row= 0)
    countdown_label.grid(row= 1)
    
def get_target_date():
    global target_datetime
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            target_date_str = file.read()
            target_datetime = datetime.strptime(target_date_str, "%Y-%m-%d %H:%M:%S")
        hour_input.insert(0,target_datetime.hour)
        minutes_input.insert(0,target_datetime.minute)
        return target_datetime
    else:
        return None    

def set_target_date():
    global target_datetime
    try:
        target_date_str = cal.get_date().strftime("%Y-%m-%d")+ " " + hour_input.get() + ":" + minutes_input.get() + ":00" 
        target_datetime = datetime.strptime(target_date_str, "%Y-%m-%d %H:%M:%S")
        if target_datetime > datetime.now():
            target_time_label.config(text="目標時間:"+target_date_str)
            with open(file_name, "w") as file:
                file.write(target_date_str)
            start_countdown()
        else:
            set_notice("時間不應該小於當前時間!")
    except ValueError:
        set_notice("時間格式錯誤")
    
def start_countdown():
    global is_start_countdown
    set_notice("開始計時!")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    is_start_countdown = True
    thread = threading.Thread(target=countdown_tread)
    thread.daemon = True
    thread.start()
        
def stop_countdown():
    global is_start_countdown
    is_start_countdown = False
    set_notice("暫停計時!")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

def countdown_tread():
    while is_start_countdown:
        current_datetime = datetime.now()
        time_remaining = target_datetime - current_datetime
        if time_remaining.total_seconds() <= 0:
            countdown_label.config(text="時間到了!")
            break
        days = time_remaining.days
        hours, remainder = divmod(time_remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        countdown_text = f"{days}天{hours}小時{minutes}分{seconds}秒"
        countdown_label.config(text="剩餘時間:" + countdown_text)
        time.sleep(1)

def set_notice(message):
    notice_label.config(text=message)
    thread = threading.Thread(target=reset_notice)
    thread.daemon = True
    thread.start()

def reset_notice():
    time.sleep(3)
    notice_label.config(text="",fg='#000000')

def main():
    global notice_label, is_start_countdown
    is_start_countdown = False
    root = tk.Tk()
    root.title('X職倒數')
    root.geometry('400x300')
    root.resizable(1, 1)
    
    notice_label = tk.Label(root)
    notice_label.pack()
    init_select_frame(root)
    init_countdown_frame(root)

    target_date = get_target_date()
    if target_date is not None:
        start_countdown()
    
    root.mainloop()
        
if __name__ == "__main__":
    main()
