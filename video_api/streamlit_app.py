import streamlit as st
import cv2
import os
import numpy as np
import tempfile
from deepface import DeepFace
from numpy.linalg import norm

# ─── Config ───────────────────────────────────────────
KNOWN_FACES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "known_faces")
MATCH_THRESHOLD = 0.55  # SFace ke liye (kam = strict)

st.set_page_config(page_title="Employee Recognition", page_icon="👤")
st.title("👥 Employee Face Recognition")
st.markdown("Video upload karo — known employees ko detect karke annotated video milegi")

# ─── Load known faces + embeddings ────────────────────

def load_recognizer():
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    known_embeddings = []

    files = [f for f in os.listdir(KNOWN_FACES_DIR) if f.endswith(".jpg")]

    for filename in files:
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
            embedding = np.array(result[0]["embedding"])
            known_embeddings.append({
                "embedding": embedding,
                "user_id": user_id,
                "name": name
            })
        except:
            pass

    return face_cascade, known_embeddings

# ─── Match function ───────────────────────────────────
def match_face(face_img, known_embeddings):
    temp_path = "temp_match.jpg"
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
            # Cosine distance
            cos_dist = 1 - np.dot(face_emb, known["embedding"]) / (
                norm(face_emb) * norm(known["embedding"]) + 1e-6
            )
            if cos_dist < best_dist:
                best_dist = cos_dist
                best_match = known

        if best_dist < MATCH_THRESHOLD:
            return best_match
    except:
        pass
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return None

# ─── App start ────────────────────────────────────────
if not os.path.exists(KNOWN_FACES_DIR):
    st.error("❌ known_faces folder nahi mila! Pehle extract_faces.py chalao.")
    st.stop()

with st.spinner("⏳ Embeddings load ho rahi hain — pehli baar thoda waqt lagega..."):
    face_cascade, known_embeddings = load_recognizer()

if not known_embeddings:
    st.error("❌ Known faces nahi mili! Pehle extract_faces.py chalao.")
    st.stop()

unique_employees = len(set(e["user_id"] for e in known_embeddings))
st.success(f"✅ {unique_employees} employees ka data loaded!")

# ─── Video Upload ─────────────────────────────────────
uploaded_file = st.file_uploader("📹 Video upload karo", type=["mp4", "avi", "mov"])

if uploaded_file:
    st.video(uploaded_file)

    if st.button("🚀 Process Karo"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
            tmp_in.write(uploaded_file.read())
            input_path = tmp_in.name

        output_path = input_path.replace(".mp4", "_output.mp4")

        # Step 1: Frames read karo
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        all_frames = []
        frame_count = 0

        progress = st.progress(0, text="Step 1: Frames read ho rahi hain...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            all_frames.append(frame.copy())
            frame_count += 1
            progress.progress(frame_count / total_frames * 0.3,
                              text=f"Step 1: Frame {frame_count}/{total_frames}")
        cap.release()

        # Step 2: Har 10th frame pe match karo
        progress.progress(0.3, text="Step 2: Faces detect + match ho rahi hain...")
        face_identities = {}

        for i, frame in enumerate(all_frames):
            if i % 10 != 0:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(detected) > 0:
                frame_detections = []
                for (x, y, w, h) in detected:
                    face_crop = frame[y:y+h, x:x+w]
                    identity = match_face(face_crop, known_embeddings)
                    frame_detections.append((x, y, w, h, identity))
                face_identities[i] = frame_detections

            progress.progress(0.3 + (i / len(all_frames)) * 0.4,
                              text=f"Step 2: Frame {i}/{len(all_frames)} match ho raha...")

        # Step 3: Annotate karo
        progress.progress(0.7, text="Step 3: Video annotate ho rahi hai...")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        recognized_people = set()

        for i, frame in enumerate(all_frames):
            if i in face_identities:
                for (x, y, w, h, identity) in face_identities[i]:
                    if identity:
                        display = f"{identity['name']} | ID: {identity['user_id']}"
                        color = (0, 255, 0)
                        recognized_people.add(f"{identity['name']} — ID: {identity['user_id']}")
                    else:
                        display = ""
                        color = (0, 0, 255)

                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    if display:
                        (tw, th), _ = cv2.getTextSize(display, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(frame, (x, y-th-10), (x+tw, y), color, -1)
                        cv2.putText(frame, display, (x, y-5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            out.write(frame)
            progress.progress(0.7 + (i / len(all_frames)) * 0.3,
                              text=f"Step 3: Frame {i+1}/{len(all_frames)}")

        out.release()
        progress.progress(1.0, text="✅ Done!")

        # Results
        st.subheader("👥 Recognized Employees:")
        if recognized_people:
            for person in recognized_people:
                st.success(f"✅ {person}")
        else:
            st.warning("⚠️ Koi known employee detect nahi hua")

        st.subheader("📹 Annotated Output Video:")
        with open(output_path, "rb") as f:
            st.video(f.read())

        with open(output_path, "rb") as f:
            st.download_button(
                label="⬇️ Output Video Download Karo",
                data=f,
                file_name="recognized_output.mp4",
                mime="video/mp4"
            )

        os.remove(input_path)
        os.remove(output_path)