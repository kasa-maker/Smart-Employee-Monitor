import cv2
from ultralytics import YOLO
import mediapipe as mp
import time
from datetime import datetime
import os
import numpy as np
from db_logger import log_mobile_usage
from attendance_logger import check_in, check_out, log_seat_absence

# ── Paths ──────────────────────────────────────────────
KNOWN_FACES_DIR = r"C:\Users\LENOVO\Desktop\VIDEO_API\video_api\known_faces"

# ── YOLO ───────────────────────────────────────────────
model = YOLO("yolov8n.pt")

# ── Face Recognition (OpenCV SFace) ────────────────────
face_detector = cv2.FaceDetectorYN.create(
    r"C:\Users\LENOVO\Desktop\VIDEO_API\mobile_detection\face_detection_yunet_2023mar.onnx",
    "", (320, 320)
)
face_recognizer = cv2.FaceRecognizerSF.create(
    r"C:\Users\LENOVO\Desktop\VIDEO_API\mobile_detection\face_recognition_sface_2021dec.onnx",
    ""
)

# ── Load Known Faces ───────────────────────────────────
print("Known faces load ho rahi hain...")
known_embeddings = []
known_names = []
known_ids = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(".jpg"):
        parts = filename.replace(".jpg", "").split("_")
        user_id = parts[0]
        name = "_".join(parts[1:-1])

        img_path = os.path.join(KNOWN_FACES_DIR, filename)
        img = cv2.imread(img_path)
        if img is None:
            continue

        h, w = img.shape[:2]
        face_detector.setInputSize((w, h))
        _, faces = face_detector.detect(img)

        if faces is not None:
            face = faces[0]
            aligned = face_recognizer.alignCrop(img, face)
            embedding = face_recognizer.feature(aligned)
            known_embeddings.append(embedding)
            known_names.append(name)
            known_ids.append(user_id)

print(f"✅ {len(known_embeddings)} face embeddings load ho gayi!")

# ── MediaPipe Hands ────────────────────────────────────
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2
)

# ── State ──────────────────────────────────────────────
is_using_mobile = False
timer_start = None
timer_start_dt = None
total_usage = 0
current_user = "Unknown"
current_id = ""

# Attendance state
checked_in_users = set()
checked_out_users = set()
last_seen = {}
away_since = {}

def get_box_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def is_close(p1, p2, threshold=150):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) ** 0.5 < threshold

def recognize_face(frame):
    h, w = frame.shape[:2]
    face_detector.setInputSize((w, h))
    _, faces = face_detector.detect(frame)

    if faces is None:
        return "Unknown", ""

    best_name = "Unknown"
    best_id = ""
    best_score = 0

    face = faces[0]
    aligned = face_recognizer.alignCrop(frame, face)
    embedding = face_recognizer.feature(aligned)

    for i, known_emb in enumerate(known_embeddings):
        score = face_recognizer.match(embedding, known_emb,
                                      cv2.FaceRecognizerSF_FR_COSINE)
        if score > best_score:
            best_score = score
            best_name = known_names[i]
            best_id = known_ids[i]

    if best_score > 0.55:
        return best_name, best_id
    return "Unknown", ""

# ── Main Loop ──────────────────────────────────────────
cap = cv2.VideoCapture(0)
frame_count = 0
print("Camera chal raha hai... Q dabaao band karne ke liye")

with HandLandmarker.create_from_options(options) as landmarker:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ── Har 10 frame pe face recognize karo ──
        if frame_count % 10 == 0:
            current_user, current_id = recognize_face(frame)
            
            if current_user != "Unknown" and current_id:
                now = datetime.now()
                
                # Check-in — pehli baar dikh raha hai
                if current_id not in checked_in_users:
                    check_in(current_id, current_user)
                    checked_in_users.add(current_id)
                
                # Seat wapas aa gaya
                if current_id in away_since:
                    away_from = away_since.pop(current_id)
                    log_seat_absence(current_id, current_user, away_from, now)
                
                last_seen[current_id] = now
            
            # 15 min se zyada koi nahi dikh raha
            for uid in list(last_seen.keys()):
                if uid not in away_since:
                    diff = (datetime.now() - last_seen[uid]).total_seconds() / 60
                    if diff > 15:
                        away_since[uid] = last_seen[uid]

        # ── YOLO detection ──
        results = model(frame, verbose=False)[0]
        mobile_center = None

        for box in results.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label == "person" and conf > 0.5:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                cv2.putText(frame, f"{current_user} ({current_id})",
                           (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (255, 255, 0), 2)

            if label == "cell phone" and conf > 0.4:
                mobile_center = get_box_center((x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"Mobile {conf:.2f}", (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # ── MediaPipe hands ──
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        hand_result = landmarker.detect(mp_image)
        hand_center = None

        if hand_result.hand_landmarks:
            for hand_landmarks in hand_result.hand_landmarks:
                cx = int(hand_landmarks[9].x * w)
                cy = int(hand_landmarks[9].y * h)
                hand_center = (cx, cy)
                cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

        # ── Mobile use logic ──
        mobile_in_use = False
        if mobile_center and hand_center:
            if is_close(mobile_center, hand_center):
                mobile_in_use = True

        # ── Timer ──
        if mobile_in_use and not is_using_mobile:
            is_using_mobile = True
            timer_start = time.time()
            timer_start_dt = datetime.now()
            print(f"📱 {current_user} ne mobile use shuru kiya!")

        elif not mobile_in_use and is_using_mobile:
            is_using_mobile = False
            end_time = datetime.now()
            elapsed = time.time() - timer_start
            total_usage += elapsed
            print(f"⏹️ {current_user} ne mobile rakha — {elapsed:.1f} sec")
            if current_user != "Unknown":
                log_mobile_usage(current_id, current_user, timer_start_dt, end_time)

        # ── Display ──
        if is_using_mobile:
            elapsed_now = time.time() - timer_start
            cv2.putText(frame, f"USING MOBILE: {elapsed_now:.1f}s",
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        else:
            cv2.putText(frame, "No Mobile Use",
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"User: {current_user} | Total: {total_usage:.1f}s",
                   (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Mobile Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Sab ka check-out
for uid in checked_in_users:
    if uid not in checked_out_users:
        name = [k for k, v in zip(known_names, known_ids) if v == uid]
        if name:
            check_out(uid, name[0])
            checked_out_users.add(uid)

cap.release()
cv2.destroyAllWindows()
print(f"\n✅ Session khatam — Total: {total_usage:.1f} seconds")