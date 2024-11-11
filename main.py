from tkinter import *
import math
from datetime import datetime
from pygame import mixer

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
COMPLETED_COLOR = "#6c757d"  # Gray color for completed tasks
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20

# ---------------------------- GLOBAL VARIABLES ------------------------- #
reps = 0
timer = None
todos = []
completed_todos = []
session_start_time = None
remaining_time = 0  # Track remaining time for resuming after stop
is_paused = False  # Check if the timer is paused


# ---------------------------- TIMER RESET ------------------------------- #
def reset_timer():
    global timer, reps, session_start_time, remaining_time, is_paused
    if timer:
        window.after_cancel(timer)
    title_lbl.config(text="Timer")
    canvas.itemconfig(timer_txt, text="00:00")
    check_marks.config(text="")
    reps = 0
    session_start_time = None
    remaining_time = 0
    is_paused = False


# ---------------------------- TIMER MECHANISM ------------------------------- #
def start_timer():
    global reps, session_start_time, remaining_time, is_paused

    if not is_paused:  # Start a new session or continue with a new interval if not paused
        reps += 1
        if reps % 2 != 0:  # Start time is set only for work sessions
            session_start_time = datetime.now()

        work_sec = WORK_MIN * 60
        short_break_sec = SHORT_BREAK_MIN * 60
        long_break_sec = LONG_BREAK_MIN * 60

        if reps == 8:
            title_lbl.config(text="Long Break", fg=RED)
            remaining_time = long_break_sec
        elif reps % 2 == 0:
            title_lbl.config(text="Short Break", fg=PINK)
            remaining_time = short_break_sec
        else:
            title_lbl.config(text="Work", fg=GREEN)
            remaining_time = work_sec

    is_paused = False  # Reset the pause status
    count_down(remaining_time)


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
def count_down(count):
    global timer, remaining_time

    count_min = math.floor(count / 60)
    count_sec = count % 60

    if count_sec < 10:
        count_sec = f"0{count_sec}"

    canvas.itemconfig(timer_txt, text=f"{count_min}:{count_sec}")

    if count > 0:
        remaining_time = count - 1  # Update remaining time for resuming
        timer = window.after(1000, count_down, count - 1)
    else:
        mixer.init()
        mixer.Sound("alarm-clock-ringing-sound.mp3").play()

        marks = ""
        work_sessions = math.floor(reps / 2)
        for _ in range(work_sessions):
            marks += "✓"
        check_marks.config(text=marks)
        remaining_time = 0  # Reset remaining time for next session
        if title_lbl.cget("text") == "Work":
            show_todo_popup()
        is_paused = False  # Reset paused state for the next interval
        start_timer()  # Automatically start next session


# ---------------------------- TODOS FUNCTIONS ------------------------------- #
def add_todo():
    todo_text = entry_txt.get()
    if todo_text:
        todos.append(todo_text)
        update_todo_display()
        entry_txt.delete(0, END)


def update_todo_display():
    for widget in todo_frame.winfo_children():
        widget.destroy()

    # Display pending todos
    for todo in todos:
        Label(todo_frame, text=todo, fg=RED, bg=YELLOW, font=(FONT_NAME, 12)).pack(anchor="w")

    # Display completed todos in a different color
    for todo, time_info in completed_todos:
        Label(todo_frame, text=f"{todo} - {time_info}", fg=COMPLETED_COLOR, bg=YELLOW, font=(FONT_NAME, 12)).pack(anchor="w")


# ---------------------------- TODO POPUP ------------------------------- #
def show_todo_popup():
    popup_win = Toplevel(window)
    popup_win.title("Check Completed Todos")
    Label(popup_win, text="Mark completed tasks:", font=(FONT_NAME, 15)).pack(pady=5)

    todo_vars = []
    for todo in todos:
        var = IntVar()
        chk = Checkbutton(popup_win, text=todo, variable=var, font=(FONT_NAME, 12), bg=YELLOW)
        chk.pack(anchor='w')
        todo_vars.append((todo, var))

    def save_checked():
        global todos, completed_todos
        session_end_time = datetime.now()
        session_duration = (session_end_time - session_start_time).seconds // 60 if session_start_time else 0

        for todo, var in todo_vars:
            if var.get() == 1:  # If checkbox is checked
                time_info = f"Started: {session_start_time.strftime('%H:%M')}, Ended: {session_end_time.strftime('%H:%M')}, Duration: {session_duration} min"
                completed_todos.append((todo, time_info))
                todos.remove(todo)
        update_todo_display()
        popup_win.destroy()

    Button(popup_win, text="Save", command=save_checked).pack(pady=10)


# ---------------------------- STOP TIMER ------------------------------- #
def stop_timer():
    global timer, is_paused
    if timer:
        window.after_cancel(timer)
        timer = None
        is_paused = True  # Set pause status to resume later


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Pomodoro")
window.config(padx=100, pady=50, bg=YELLOW)

title_lbl = Label(fg=GREEN, bg=YELLOW, text="Timer", font=(FONT_NAME, 30))
title_lbl.grid(row=0, column=1)

canvas = Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = PhotoImage(file="tomato.png")
canvas.create_image(100, 112, image=tomato_img)
timer_txt = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 35, "bold"))
canvas.grid(row=1, column=1, columnspan=2)

start_btn = Button(text="Start", highlightbackground=YELLOW, command=start_timer)
start_btn.grid(row=2, column=0)

stop_btn = Button(text="Stop", highlightbackground=YELLOW, command=stop_timer)
stop_btn.grid(row=2, column=2)

reset_btn = Button(text="Reset", highlightbackground=YELLOW, command=reset_timer)
reset_btn.grid(row=2, column=3)

check_marks = Label(fg=GREEN, bg=YELLOW)
check_marks.grid(row=3, column=1)

todo_lbl = Label(text="TODO's", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 20))
todo_lbl.grid(row=4, column=1)

entry_txt = Entry(window)
entry_txt.grid(row=5, column=1)

add_btn = Button(text="Add Todo", command=add_todo)
add_btn.grid(row=5, column=2)

todo_frame = Frame(window, bg=YELLOW)
todo_frame.grid(row=6, column=1, columnspan=2, pady=10)

window.mainloop()
