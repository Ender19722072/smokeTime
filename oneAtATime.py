import logging
import tkinter as tk
import time
import os
import threading
from datetime import datetime
import signal
import sys

# Prometheus
from prometheus_client import start_http_server, Gauge

# Metrics
popup_count_last_day = Gauge("smoketime_popups_last_24h", "Number of popups in last 24 hours")
user_close_delay = Gauge("smoketime_user_close_delay_seconds", "Seconds user takes to close popup")

popup_timestamps = []

# GLOBAL POPUP LOCK + FLAG
popup_lock = threading.Lock()
popup_active = False   # <<< NEW FLAG

def now_local():
    return datetime.now()

def record_popup_event():
    now = time.time()
    popup_timestamps.append(now)
    cutoff = now - 24 * 60 * 60
    recent = [t for t in popup_timestamps if t >= cutoff]
    popup_timestamps[:] = recent
    popup_count_last_day.set(len(recent))

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
            f.write(now_local().strftime(TIME_FORMAT))

def write_last_smoke_time():
    timestamp = now_local().strftime(TIME_FORMAT)
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

# POPUP TEMPLATE
def popup_window(title, message, bg_color, fg_color="black"):
    global popup_active

    with popup_lock:
        if popup_active:
            print("[INFO] Popup blocked because another popup is active.")
            return

        popup_active = True  # <<< FLAG SET

    start_time = time.time()

    root = tk.Tk()
    root.title(title)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (WINDOW_WIDTH // 2)
    y = (screen_height // 2) - (WINDOW_HEIGHT // 2)

    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    root.configure(bg=bg_color)

    label = tk.Label(root, text=message, font=("Arial", 16, "bold"), bg=bg_color, fg=fg_color)
    label.pack(expand=True)

    def on_close(event=None):
        global popup_active
        end_time = time.time()
        delay = end_time - start_time
        user_close_delay.set(delay)
        popup_active = False  # <<< FLAG RELEASED
        root.destroy()

    root.bind("<Button-1>", on_close)
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()

    record_popup_event()

def show_smoke_popup():
    popup_window("SmokeTime Reminder", "Time for a smoke break!", "lightgray")
    write_last_smoke_time()

def show_eat_popup():
    popup_window("Lunch Reminder", "Time to Eat!", "green", "white")

def show_fruit_popup():
    popup_window("Fruit Reminder", "Time for fruit!", "orange", "white")

# ASYNC WRAPPERS
def show_smoke_popup_async():
    threading.Thread(target=show_smoke_popup, daemon=True).start()

def show_eat_popup_async():
    threading.Thread(target=show_eat_popup, daemon=True).start()

def show_fruit_popup_async():
    threading.Thread(target=show_fruit_popup, daemon=True).start()

# COUNTDOWN
def seconds_to_mmss(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}m {sec:02d}s"

def print_countdown_loop(last_smoke_time):
    now = now_local()
    elapsed = int((now - last_smoke_time).total_seconds())
    remaining = SMOKE_INTERVAL_MINUTES * 60 - elapsed
    if remaining < 0:
        remaining = 0

    print(
        f"[STATUS] Since last break: {seconds_to_mmss(elapsed)} | "
        f"Until next break: {seconds_to_mmss(remaining)}"
    )

# STARTUP
print(f"Smoke reminder is running every {SMOKE_INTERVAL_MINUTES} minutes...")

start_http_server(8000)

write_first_smoke_time()
write_last_smoke_time()
create_heartbeat()

last_lunch_day = None
FRUIT_INTERVAL_SECONDS = 3 * 60 * 60

last_fruit_time = now_local()

# MAIN LOOP
try:
    last_smoke_time = now_local()

    while True:
        total_seconds = SMOKE_INTERVAL_MINUTES * 60
        steps = total_seconds // 5

        for _ in range(steps):
            now = now_local()

            # DAILY 12:00 CHECK
            if now.hour == LAUNCH_TIME and now.minute == 0:
                if last_lunch_day != now.date():
                    show_eat_popup_async()
                    last_lunch_day = now.date()

            # FRUIT LOGIC
            if 11 <= now.hour < 13:
                last_fruit_time = now
            else:
                elapsed_fruit = (now - last_fruit_time).total_seconds()
                if elapsed_fruit >= FRUIT_INTERVAL_SECONDS:
                    show_fruit_popup_async()
                    last_fruit_time = now

            print_countdown_loop(last_smoke_time)
            time.sleep(5)

        show_smoke_popup_async()
        last_smoke_time = now_local()

finally:
    cleanup_heartbeat()
