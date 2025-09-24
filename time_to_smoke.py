#!/usr/bin/env python3
from datetime import datetime, timedelta
import os
import sys

SMOKE_INTERVAL_MINUTES = 60
LAST_FILE = os.path.expanduser("~/.last_smoke_time")
FIRST_FILE = os.path.expanduser("~/.first_smoke_time")
TIME_FORMAT = "%A, %d %B %Y at %H:%M:%S"

def read_time(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return datetime.strptime(f.read().strip(), TIME_FORMAT)
    except:
        return None

def time_to_next_smoke(last_time):
    if not last_time:
        return "No previous smoke break recorded."
    next_time = last_time + timedelta(minutes=SMOKE_INTERVAL_MINUTES)
    remaining = next_time - datetime.now()
    if remaining.total_seconds() <= 0:
        return "You can smoke now! ?"
    minutes = int(remaining.total_seconds() // 60)
    seconds = int(remaining.total_seconds() % 60)
    return f"{minutes} minute(s) and {seconds} second(s) until your next smoke break."

def time_since_first_smoke(first_time):
    if not first_time:
        return "No first smoke break recorded."
    elapsed = datetime.now() - first_time
    minutes = int(elapsed.total_seconds() // 60)
    return f"{minutes} minute(s) since your first smoke break."

if __name__ == "__main__":
    last = read_time(LAST_FILE)
    first = read_time(FIRST_FILE)

    print(time_to_next_smoke(last))
    print(time_since_first_smoke(first))
