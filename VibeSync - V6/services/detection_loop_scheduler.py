import json
import os
import threading
from datetime import datetime, timedelta
from services.emotion import detect_emotion
from services.activity import get_activity_snapshot
from services.groqapi import fetch_motivational_quote
from services.notification import show_notification
from services.quotes import fallback_quote
import psutil
import cv2
from PyQt5.QtCore import QObject, pyqtSignal
from windows_toasts import Toast, WindowsToaster

class EmotionScheduler(QObject):
    scheduler_ready = pyqtSignal()
    LOG_FILE = "data/log.json"

    def __init__(self):
        super().__init__()
        self.start_time = None
        self.thread = None
        self.running = False
        self.timer = None
        self.lock = threading.Lock()
        self.camera_lock = threading.Lock()
        self.next_trigger_time = None
        os.makedirs("data", exist_ok=True)

    def load_schedule(self):
        with open("settings.json") as f:
            settings = json.load(f)
        schedule = settings["monitoring_schedule"]
        print(f"[Debug] Loaded schedule: '{schedule}'")
        return self.get_interval_minutes(schedule)

    def get_interval_minutes(self, schedule):
        schedule = schedule.lower().strip()
        if schedule == "every 30 seconds":
            return 0.5
        elif schedule == "every 1 minute":
            return 1
        elif schedule == "every 2 minutes":
            return 2
        elif schedule == "every 4 minutes":
            return 4
        elif schedule == "every 30 minutes":
            return 30
        elif schedule == "hourly":
            return 60
        elif schedule == "every 2 hours":
            return 120
        elif schedule == "every 3 hours":
            return 180
        else:
            return 60

    def start_emotion_scheduler(self):
        if self.running:
            print("[Debug] Scheduler already running.")
            return
        self.start_time = datetime.now()
        self.running = True
        self.schedule_next_detection()

    def schedule_next_detection(self):
        interval = self.load_schedule()
        self.next_trigger_time = datetime.now() + timedelta(minutes=interval)
        now = datetime.now()
        wait_time = (self.next_trigger_time - now).total_seconds()

        print(f"Next detection at: {self.next_trigger_time.strftime('%H:%M:%S')} (in {wait_time/60:.1f} mins)")

        self.timer = threading.Timer(wait_time, self.run_detection_cycle)
        self.timer.start()

    def run_detection_cycle(self):
        with self.lock:
            if not self.running:  # <<< CHECK IF STOPPED
                print("[Debug] Scheduler stopped. Exiting detection cycle.")
                return
    
            print(f"Emotion detection triggered at {datetime.now().strftime('%H:%M:%S')}")

            # Check conditions first
            if self.is_user_in_video_conference():
                message = "Video call detected. Skipping detection..."
                show_notification("VibeSync Motivation", message)
                self.schedule_next_detection()
                return
            elif not self.is_face_found():
                message = "Face not found, Are you on a break?"
                show_notification("VibeSync Motivation", message)
                self.schedule_next_detection()
                return
            
            self.perform_emotion_detection()
            self.start_time = datetime.now()
            self.schedule_next_detection()


    def is_user_in_video_conference(self):
        video_apps = ["zoom", "teams", "skype", "meet", "webex", "discord"]
        using_video_call = False

        try:
            for proc in psutil.process_iter(['name']):
                try:
                    pname = proc.info['name'].lower()
                    if any(app in pname for app in video_apps):
                        print(f"[Debug] Video conferencing app running: {pname}")
                        using_video_call = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Additional check for camera status regardless of process detection
            with self.camera_lock:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("[Debug] Camera cannot be opened")
                    return True
                
                ret, _ = cap.read()
                cap.release()

                if not ret:
                    print("[Debug] Camera busy")
                    return True
                else:
                    print("[Debug] Camera available")
                    return using_video_call  # Only return True if we detected both app and busy camera

        except Exception as e:
            print(f"[Error] Camera check failed: {str(e)}")
            return False  # Default to False if we can't determine status

    # def is_user_in_video_conference(self):
    #     video_apps = ["zoom", "teams", "skype", "meet", "webex", "discord"]
    #     using_video_call = False

    #     for proc in psutil.process_iter(['name']):
    #         try:
    #             pname = proc.info['name'].lower()
    #             if any(app in pname for app in video_apps):
    #                 print(f"[Debug] Video conferencing app running: {pname}")
    #                 using_video_call = True
    #                 break
    #         except (psutil.NoSuchProcess, psutil.AccessDenied):
    #             continue

    #     if using_video_call:
    #         with self.camera_lock:
    #             # Try accessing webcam
    #             cap = cv2.VideoCapture(0)
    #             ret, _ = cap.read()
    #             cap.release()

    #         if not ret:
    #             print("[Debug] Camera busy – likely in use by video call")
    #             return True  # Skip emotion detection
    #         else:
    #             print("[Debug] Camera available – proceed with emotion detection")
    #             return False
    #     return False

    def is_face_found(self):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        cap = cv2.VideoCapture(0)
        try:
            ret, frame = cap.read()
        finally:
            cap.release()

        if not ret:
            print("[Debug] Couldn't access webcam.")
            return False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        face_found = len(faces) > 0
        print(f"[Debug] Face detection: {'Found' if face_found else 'Not Found'}")
        return face_found

    def log_entry(self, entry):
        try:
            if os.path.exists(self.LOG_FILE):
                with open(self.LOG_FILE, 'r') as f:
                    data = json.load(f)
            else:
                data = []
        except:
            data = []

        data.append(entry)
        with open(self.LOG_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def perform_emotion_detection(self):
        print("[VibeSync] Background monitoring started...")
        try:
            print("[VibeSync] Running snapshot analysis...")

            emotion = detect_emotion()
            activity = get_activity_snapshot()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Prepare payload for Groq
            user_state = {
                "timestamp": timestamp,
                "emotion": emotion,
                "activity": activity
            }

            quote = fetch_motivational_quote(user_state)
            if not quote:
                quote = fallback_quote(emotion)

            show_notification("VibeSync Motivation", quote)

            self.log_entry({
                "timestamp": timestamp,
                "emotion": emotion,
                "activity": activity,
                "quote": quote
            })

        except Exception as e:
            print(f"[VibeSync Error] {e}")

    def stop(self):
        self.running = False
        if self.timer:
            self.timer.cancel()
            self.timer = None
            print("[Debug] Timer cancelled.")
        print("[Debug] EmotionScheduler stopped by user.")

    def get_next_trigger_time(self):
        if self.next_trigger_time:
            return self.next_trigger_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return "Not scheduled yet"

