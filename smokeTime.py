#!/usr/bin/env python3
import logging
import tkinter as tk
import time
import os
import threading
from datetime import datetime
import signal
import sys

def handle_interrupt(sig, frame):
    logging.info("SmokeTime manually interrupted by user.")
    print("SmokeTime interrupted. Exiting.")
    cleanup_heartbeat()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

# CONFIGURATION
SMOKE_INTERVAL_MINUTES = 60
LAUNCH_TIME = 12
WINDOW_WIDTH = 750
WINDOW_HEIGHT = 100
TIME_FORMAT = "%A, %d %B %Y at %H:%M:%S"

# File paths
LAST_FILE = os.path.expanduser("~/.last_smoke_time")
FIRST_FILE = os.path.expanduser("~/.first_smoke_time")
HEARTBEAT = os.path.expanduser("~/.smoketime_running")

logging.basicConfig(
    filename='smokeTime.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%A, %d %B %Y at %H:%M:%S'
)

def write_first_smoke_time():
    if not os.path.exists(FIRST_FILE):
        with open(FIRST_FILE, "w") as f:
            f.write(datetime.now().strftime(TIME_FORMAT))

def write_last_smoke_time():
    timestamp = datetime.now().strftime(TIME_FORMAT)
    try:
        with open(LAST_FILE, "w") as f:
            f.write(timestamp)
        print(f"[INFO] Last smoke time written: {timestamp}")
    except Exception as e:
        print(f"[ERROR] Failed to write last smoke time: {e}")

def create_heartbeat():
    with open(HEARTBEAT, "w") as f:
        f.write("running")

def cleanup_heartbeat():
    if os.path.exists(HEARTBEAT):
        os.remove(HEARTBEAT)

# ---------------------------------------------------------
# SOUND DISABLED ? LEFT HERE FOR FUTURE USE
# ---------------------------------------------------------
# def play_sound_async():
#     def run():
#         os.system("aplay n_sound.mp3 >/dev/null 2>&1")
#     threading.Thread(target=run, daemon=True).start()
# ---------------------------------------------------------

def show_smoke_popup():
    root = tk.Tk()
    root.title("SmokeTime Reminder")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (WINDOW_WIDTH // 2)
    y = (screen_height // 2) - (WINDOW_HEIGHT // 2)

    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    root.configure(bg="lightgray")

    label = tk.Label(root, text="Time for a smoke break!", font=("Arial", 14), bg="lightgray")
    label.pack(expand=True)

    root.bind("<Button-1>", lambda e: root.destroy())

    # SOUND DISABLED
    # play_sound_async()

    root.mainloop()
    write_last_smoke_time()

# ---------------------------------------------------------
# NEW: DAILY 12:00 NOON POPUP
# ---------------------------------------------------------
def show_eat_popup():
    root = tk.Tk()
    root.title("Lunch Reminder")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (WINDOW_WIDTH // 2)
    y = (screen_height // 2) - (WINDOW_HEIGHT // 2)

    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    root.configure(bg="green")

    label = tk.Label(root, text="Time to Eat!", font=("Arial", 18, "bold"), bg="green", fg="white")
    label.pack(expand=True)

    root.bind("<Button-1>", lambda e: root.destroy())
    root.mainloop()

# -----------------------------
# COUNTDOWN FUNCTIONS
# -----------------------------
def seconds_to_mmss(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}m {sec:02d}s"

def print_countdown_loop(last_smoke_time):
    now = datetime.now()
    elapsed = int((now - last_smoke_time).total_seconds())
    remaining = SMOKE_INTERVAL_MINUTES * 60 - elapsed
    if remaining < 0:
        remaining = 0

    print(
        f"[STATUS] Since last break: {seconds_to_mmss(elapsed)} | "
        f"Until next break: {seconds_to_mmss(remaining)}"
    )

# Startup
print(f"Smoke reminder is running every {SMOKE_INTERVAL_MINUTES} minutes...")
write_first_smoke_time()
write_last_smoke_time()
create_heartbeat()

# Track whether today's lunch popup has been shown
last_lunch_day = None

# Main loop with 5-second countdown printing
try:
    last_smoke_time = datetime.now()

    while True:
        total_seconds = SMOKE_INTERVAL_MINUTES * 60
        steps = total_seconds // 5

        for _ in range(steps):
            now = datetime.now()

            # DAILY 12:00 CHECK
            if now.hour == LAUNCH_TIME and now.minute == 0:
                if last_lunch_day != now.date():
                    show_eat_popup()
                    last_lunch_day = now.date()

            print_countdown_loop(last_smoke_time)
            time.sleep(5)

        show_smoke_popup()
        last_smoke_time = datetime.now()

finally:
    cleanup_heartbeat()
