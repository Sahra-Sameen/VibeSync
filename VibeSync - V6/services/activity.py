from pynput import keyboard, mouse
from threading import Thread
from time import time, sleep
import win32gui
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Global state trackers
typing_count = 0
mouse_distance = 0
last_mouse_pos = None

# Start time for activity snapshot
start_time = time()

# --- Keyboard Listener ---
def on_key_press(key):
    global typing_count
    typing_count += 1

# --- Mouse Listener ---
def on_mouse_move(x, y):
    global last_mouse_pos, mouse_distance
    if last_mouse_pos:
        dx = abs(x - last_mouse_pos[0])
        dy = abs(y - last_mouse_pos[1])
        mouse_distance += (dx**2 + dy**2)**0.5
    last_mouse_pos = (x, y)

# --- Foreground Window ---
def get_foreground_window():
    try:
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        return title if title else "Untitled"
    except Exception as e:
        logging.warning(f"[Window] Error retrieving active window: {e}")
        return "Unknown"

# --- Activity Snapshot ---
def get_activity_snapshot():
    global typing_count, mouse_distance, start_time
    end_time = time()
    duration = max(end_time - start_time, 1)

    snapshot = {
        "typing_speed": round(typing_count / duration, 2),   # keys/sec
        "mouse_speed": round(mouse_distance / duration, 2),  # pixels/sec
        "active_window": get_foreground_window()
    }

    # Reset counters
    typing_count = 0
    mouse_distance = 0
    start_time = time()

    logging.info(f"[Activity] Snapshot: {snapshot}")
    return snapshot

# --- Background Listeners ---
def start_listeners():
    Thread(target=lambda: keyboard.Listener(on_press=on_key_press).run(), daemon=True).start()
    Thread(target=lambda: mouse.Listener(on_move=on_mouse_move).run(), daemon=True).start()

# Start listeners on import
start_listeners()
