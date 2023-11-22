import os
import time
import tkinter as tk
import threading
from datetime import datetime
from tkcalendar import DateEntry
from babel.numbers import format_decimal

file_name = "data"

def init_select_frame(root):
    global cal, title_input,hour_input, minutes_input, start_button, stop_button
        
    select_frame = tk.Frame(root)
    title_label = tk.Label(select_frame, text="標題:")
    title_input = tk.Entry(select_frame)
    cal = DateEntry(select_frame, selectmode = 'day', width=30, date_pattern="yyyy/mm/dd")
    time_label = tk.Label(select_frame, text="時間:")
    hour_input = tk.Entry(select_frame, width=5)
    split_label = tk.Label(select_frame, text=":")
    minutes_input = tk.Entry(select_frame, width=5)
    
    start_button = tk.Button(select_frame, text="開始倒數", width=12, command=set_target_date)
    stop_button = tk.Button(select_frame, text="停止倒數", width=12, command=stop_countdown, state=tk.DISABLED)
 
    select_frame.pack()
    title_label.grid(row=0, column=0)
    title_input.grid(row=0, column=1, columnspan=4)
    cal.grid(row=1, columnspan=5, padx=10, pady=10, sticky='w')
    time_label.grid(row=2, column=0, padx=10)
    hour_input.grid(row=2, column=1, padx=10)
    split_label.grid(row=2, column=2)
    minutes_input.grid(row=2, column=3, padx=10)
    start_button.grid(row=3,column=0,columnspan=2, padx=10)
    stop_button.grid(row=3,column=3,columnspan=2, padx=10)
    return select_frame

def init_countdown_frame(root):
    global target_time_label, countdown_label
    countdown_frame = tk.Frame(root)
    target_time_label = tk.Label(countdown_frame, text="目標時間:未設定")
    countdown_label = tk.Label(countdown_frame, text="剩餘時間:00天00小時00分00秒")
    
    countdown_frame.pack()
    target_time_label.grid(row= 0)
    countdown_label.grid(row= 1)
    
def get_target_date():
    global target_datetime
    if os.path.exists(file_name):
        with open(file_name, "r", encoding='utf-8') as file:
            lines= file.readlines()
            target_date_str = lines[0].strip()
            if 1 in range(len(lines)):
                title_str = lines[1]
            else:
                title_str = '倒數計時小工具'
            target_datetime = datetime.strptime(target_date_str, "%Y-%m-%d %H:%M:%S")
        root.title(title_str)
        title_input.insert(0,title_str)
        title_input.config(state=tk.DISABLED)
        hour_input.insert(0,target_datetime.hour)
        minutes_input.insert(0,target_datetime.minute)
        cal.set_date(target_datetime)
        return target_datetime
    else:
        return None    

def set_target_date():
    global target_datetime
    try:
        text_string = cal.get_date().strftime("%Y-%m-%d")+ " " + hour_input.get() + ":" + minutes_input.get() + ":00" 
        target_datetime = datetime.strptime(text_string, "%Y-%m-%d %H:%M:%S")
        text_string = text_string + "\n" + title_input.get()
        print(title_input.get())
        if target_datetime > datetime.now():
            with open(file_name, "w", encoding='utf-8') as file:
                file.write(text_string)
            root.title(title_input.get())
            title_input.config(state=tk.DISABLED)
            start_countdown()
        else:
            set_notice("時間不應該小於當前時間!")
    except ValueError:
        set_notice("時間格式錯誤")
    
def start_countdown():
    global is_start_countdown
    set_notice("開始計時!")
    target_time_label.config(text="目標時間:"+target_datetime.strftime("%Y-%m-%d %H:%M:%S"))
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    cal.config(state=tk.DISABLED)
    hour_input.config(state=tk.DISABLED)
    minutes_input.config(state=tk.DISABLED)
    is_start_countdown = True
    thread = threading.Thread(target=countdown_tread)
    thread.daemon = True
    thread.start()
        
def stop_countdown():
    global is_start_countdown
    is_start_countdown = False
    set_notice("暫停計時!")
    title_input.config(state=tk.NORMAL)
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    cal.config(state=tk.NORMAL)
    hour_input.config(state=tk.NORMAL)
    minutes_input.config(state=tk.NORMAL)
    target_time_label.config(text="目標時間:未設定")
    countdown_label.config(text="剩餘時間:00天00小時00分00秒")

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
        
        countdown_text = f"{days:02d}天{hours:02d}小時{minutes:02d}分{seconds:02d}秒"
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
    global root, notice_label, is_start_countdown
    is_start_countdown = False
    root = tk.Tk()
    root.title('倒數計時小工具')
    root.geometry('250x250')
    root.resizable(1, 1)
    
    notice_label = tk.Label(root)
    notice_label.pack(pady=5)
    init_select_frame(root)
    init_countdown_frame(root)

    target_date = get_target_date()
    if target_date is not None:
        start_countdown()
    
    root.mainloop()
        
if __name__ == "__main__":
    main()
