import cv2
import os
from deepface import DeepFace
from database import SessionLocal
from models import UserVideo

os.makedirs("known_faces", exist_ok=True)

def extract_faces_from_db():
    db = SessionLocal()
    users = db.query(UserVideo).all()

    for user in users:
        print(f"Processing: {user.name} (ID: {user.user_id})")

        # Video temp save karo
        temp_video = f"temp_{user.user_id}.mp4"
        with open(temp_video, "wb") as f:
            f.write(user.video_data)

        cap = cv2.VideoCapture(temp_video)
        saved_count = 0
        frame_count = 0
        max_faces = 15

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 5 != 0:
                continue

            # Temp frame save karo
            temp_frame = f"temp_frame_{user.user_id}.jpg"
            cv2.imwrite(temp_frame, frame)

            try:
                # DeepFace se face detect karo
                faces = DeepFace.extract_faces(
                    img_path=temp_frame,
                    enforce_detection=True,
                    detector_backend='opencv'
                )

                if faces:
                    # Face crop karke save karo
                    facial_area = faces[0]['facial_area']
                    x = facial_area['x']
                    y = facial_area['y']
                    w = facial_area['w']
                    h = facial_area['h']

                    padding = 20
                    y1 = max(0, y - padding)
                    y2 = min(frame.shape[0], y + h + padding)
                    x1 = max(0, x - padding)
                    x2 = min(frame.shape[1], x + w + padding)
                    face_crop = frame[y1:y2, x1:x2]
                    face_crop = cv2.resize(face_crop, (160, 160))
                    save_path = f"known_faces/{user.user_id}_{user.name}_{saved_count}.jpg"
                    cv2.imwrite(save_path, face_crop)
                    print(f"  ✅ Face saved: {save_path}")
                    saved_count += 1

            except Exception as e:
                pass  # Face nahi mila is frame mein

            finally:
                if os.path.exists(temp_frame):
                    os.remove(temp_frame)

            if saved_count >= max_faces:
                break

        cap.release()
        if os.path.exists(temp_video):
            os.remove(temp_video)

        if saved_count == 0:
            print(f"  ❌ Koi face nahi mila: {user.name}")
        else:
            print(f"  ✅ {saved_count} faces saved: {user.name}")

    db.close()
    print("\n✅ Sab complete!")

if __name__ == "__main__":
    extract_faces_from_db()