Ab README update karte hain. README.md ka poora content replace karo:
markdown# 🧠 Smart Employee Monitor

A complete real-time employee monitoring system with face recognition, mobile usage tracking, and attendance management.

---

## 📁 Project Structure
smart-employee-monitor/
├── video_api/                  # Face Recognition & Attendance
│   ├── main.py                 # FastAPI backend
│   ├── recognize.py            # Live face recognition
│   ├── extract_faces.py        # Face extraction from DB
│   ├── streamlit_app.py        # Video upload dashboard
│   ├── database.py             # DB connection
│   ├── models.py               # DB models
│   └── camera.html             # Camera UI
│
└── mobile_detection/           # Mobile Usage & Attendance
├── mobile_detection.py     # Live mobile + face detector
├── db_logger.py            # Mobile usage logging
├── attendance_logger.py    # Check-in/out + seat absence
└── dashboard.py            # Streamlit dashboard

---

## ✅ Features

### 👤 Face Recognition
- Upload employee video via browser
- Automatic face extraction from video
- Live camera face recognition
- Employee data stored in PostgreSQL

### 📱 Mobile Detection
- Mobile phone detection using YOLOv8
- Hand tracking using MediaPipe
- Timer to track mobile usage duration
- Detects only when mobile is actively being used

### ✅ Attendance Management
- Auto check-in when employee is detected
- Auto check-out when system is closed
- Tracks total hours worked

### 🪑 Seat Monitoring
- Detects when employee leaves seat
- Logs absence if away for 15+ minutes
- Records away time and duration

### 📊 Real-time Dashboard
- Attendance report
- Mobile usage report
- Seat absence report
- CSV download for all reports

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
git clone https://github.com/kasa-maker/smart-employee-monitor.git
cd smart-employee-monitor
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
# Terminal 1 - Detection System
cd mobile_detection
python mobile_detection.py

# Terminal 2 - Dashboard
cd mobile_detection
streamlit run dashboard.py

# Terminal 3 - Face Recognition API
cd video_api
uvicorn main:app --reload

# Terminal 4 - Ngrok
ngrok http 8000
```

---

## 🗄️ Database Tables

| Table | Purpose |
|---|---|
| user_videos | Stores employee videos |
| mobile_usage | Logs mobile usage sessions |
| attendance | Check-in/out records |
| seat_absence | Seat absence logs (15+ min) |

---

## 📊 How It Works
Camera Feed
↓
YOLOv8 detects person + mobile phone
↓
Face recognized → Employee identified
↓
Auto Check-in saved to database
↓
MediaPipe tracks hand position
↓
If hand close to mobile → Timer starts
↓
If away from seat 15+ min → Absence logged
↓
Dashboard shows real-time report

---

## ⚠️ Important Notes
- Never share your `.env` file
- Model files are not included — download automatically
- Run `extract_faces.py` when new employee data is added
- Minimum 15 face images recommended per employee
