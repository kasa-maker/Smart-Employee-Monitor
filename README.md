# 👁️ Employee Face Recognition & Mobile Detection System

A complete employee monitoring system with face recognition, mobile usage tracking, and attendance management.

---

## 📁 Project Structure
VIDEO_API/
├── video_api/              # Face Recognition & Attendance
│   ├── main.py             # FastAPI backend
│   ├── recognize.py        # Live face recognition
│   ├── extract_faces.py    # Face extraction from DB
│   ├── streamlit_app.py    # Video upload dashboard
│   ├── database.py         # DB connection
│   ├── models.py           # DB models
│   └── camera.html         # Camera UI
│
└── mobile_detection/       # Mobile Usage Tracking
├── mobile_detection.py # Live mobile detector
├── db_logger.py        # Database logging
└── dashboard.py        # Streamlit dashboard

---

## ✅ Features

### 👤 Face Recognition System
- Upload employee video via browser
- Automatic face extraction from video
- Live camera face recognition
- Employee data stored in PostgreSQL

### 📱 Mobile Detection System
- Mobile phone detection using YOLOv8
- Hand tracking using MediaPipe
- Timer to track mobile usage duration
- Real-time dashboard with usage reports

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Backend | FastAPI |
| Database | PostgreSQL (Neon Cloud) |
| Face Detection | OpenCV YuNet |
| Face Recognition | SFace Model |
| Object Detection | YOLOv8 |
| Hand Tracking | MediaPipe |
| Frontend | Streamlit, HTML/JS |
| Tunnel | Ngrok |

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kasa-maker/Employee-Face-Recognition-Mobile-Detection.git
cd Employee-Face-Recognition-Mobile-Detection
```

### 2. Environment Variables
```bash
cp .env.example .env
# Add your Neon Cloud DATABASE_URL in .env file
```

### 3. Video API Setup
```bash
cd video_api
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Mobile Detection Setup
```bash
cd mobile_detection
python -m venv venv
venv\Scripts\activate
pip install ultralytics mediapipe opencv-python psycopg2-binary streamlit python-dotenv

# Download required models
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

---

## 🔄 Daily Usage

```bash
# Terminal 1 - Face Recognition API
cd video_api
uvicorn main:app --reload

# Terminal 2 - Mobile Detection
cd mobile_detection
python mobile_detection.py

# Terminal 3 - Dashboard
cd mobile_detection
streamlit run dashboard.py

# Terminal 4 - Ngrok (for remote access)
ngrok http 8000
```

---

## 🗄️ Database Tables

| Table | Purpose |
|---|---|
| user_videos | Stores employee videos |
| mobile_usage | Logs mobile usage sessions |

---

## 📊 How It Works
Camera Feed
↓
YOLOv8 detects person + mobile phone
↓
MediaPipe tracks hand position
↓
If hand is close to mobile → Timer starts
↓
Face recognized → Employee identified
↓
Session saved to PostgreSQL
↓
Dashboard shows real-time report

---

## ⚠️ Important Notes
- Never share your `.env` file
- Model files (`.onnx`, `.pt`, `.task`) are downloaded automatically
- Run `extract_faces.py` whenever new employee data is added
- Minimum 15 face images recommended per employee for best accuracy