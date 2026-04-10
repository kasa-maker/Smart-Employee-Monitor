import cv2
import os
import numpy as np
from deepface import DeepFace
from numpy.linalg import norm

KNOWN_FACES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "known_faces")
MATCH_THRESHOLD = 0.55
PROCESS_EVERY = 5  # Har 5th frame pe match karo

# ─── Embeddings load karo ─────────────────────────────
print("📂 Known faces load ho rahi hain...")

known_embeddings = []
for filename in os.listdir(KNOWN_FACES_DIR):
    if not filename.endswith(".jpg"):
        continue
    parts = filename.replace(".jpg", "").split("_")
    user_id = parts[0]
    name = "_".join(parts[1:-1])
    fpath = os.path.join(KNOWN_FACES_DIR, filename)
    try:
        result = DeepFace.represent(
            img_path=fpath,
            model_name="SFace",
            enforce_detection=False,
            detector_backend="opencv"
        )
        known_embeddings.append({
            "embedding": np.array(result[0]["embedding"]),
            "user_id": user_id,
            "name": name
        })
    except:
        pass

print(f"✅ {len(set(e['user_id'] for e in known_embeddings))} employees loaded!")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def match_face(face_img):
    temp_path = "temp_live.jpg"
    cv2.imwrite(temp_path, face_img)
    try:
        result = DeepFace.represent(
            img_path=temp_path,
            model_name="SFace",
            enforce_detection=False,
            detector_backend="skip"
        )
        face_emb = np.array(result[0]["embedding"])
        best_match = None
        best_dist = float("inf")
        for known in known_embeddings:
            cos_dist = 1 - np.dot(face_emb, known["embedding"]) / (
                norm(face_emb) * norm(known["embedding"]) + 1e-6
            )
            if cos_dist < best_dist:
                best_dist = cos_dist
                best_match = known
        if best_dist < MATCH_THRESHOLD:
            return best_match, best_dist
    except:
        pass
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return None, None

# ─── Live Camera ──────────────────────────────────────
cap = cv2.VideoCapture(0)
print("🎥 Camera on — Esc dabao band karne ke liye")

frame_count = 0
last_results = []  # Last detection results cache

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detected = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Har 5th frame pe match karo
    if frame_count % PROCESS_EVERY == 0:
        last_results = []
        for (x, y, w, h) in detected:
            face_crop = frame[y:y+h, x:x+w]
            identity, dist = match_face(face_crop)
            last_results.append((x, y, w, h, identity))

    # Last results draw karo har frame pe
    for (x, y, w, h, identity) in last_results:
        if identity:
            display = f"{identity['name']} | ID: {identity['user_id']}"
            color = (0, 255, 0)
        else:
            display = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        (tw, th), _ = cv2.getTextSize(display, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x, y-th-10), (x+tw, y), color, -1)
        cv2.putText(frame, display, (x, y-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imshow("Employee Recognition - Live", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
if os.path.exists("temp_live.jpg"):
    os.remove("temp_live.jpg")