from deepface import DeepFace
import cv2
import os
from datetime import datetime

SNAPSHOT_DIR = "data/snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def save_snapshot(frame, timestamp):
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"{timestamp}.jpg")
    cv2.imwrite(snapshot_path, frame)
    print(f"[Snapshot] Saved: {snapshot_path}")
    return snapshot_path

def detect_emotion():
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()

        if not ret:
            raise RuntimeError("Failed to capture webcam frame.")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_snapshot(frame, timestamp)

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        except Exception as inner_e:
            print(f"[DeepFace Warning] Primary analysis failed, trying grayscale. Error: {inner_e}")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            result = DeepFace.analyze(gray, actions=['emotion'], enforce_detection=False)

        if isinstance(result, list):
            result = result[0]

        emotion = result.get('dominant_emotion', 'neutral')
        confidence = result.get('emotion', {}).get(emotion, None)

        print(f"[Emotion] {emotion} (confidence: {confidence}%)")

        return emotion

    except Exception as e:
        print(f"[Emotion Error] {e}")
        return "neutral"
