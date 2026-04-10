# 🎯 ID and Face Detection System

A real-time employee face recognition system built with FastAPI, PostgreSQL, DeepFace, and Streamlit.

## 🚀 Features
- 📹 Employee video recording via browser camera
- ☁️ Video storage in Neon Cloud PostgreSQL
- 🤖 Face extraction using DeepFace (SFace Model)
- 🎯 Real-time face recognition — live camera + video upload
- 📊 Annotated output video with Name and ID labels
- 🌐 Shareable link via Ngrok

## 🛠️ Tech Stack
- **Backend:** FastAPI, PostgreSQL (Neon Cloud)
- **AI/ML:** DeepFace (SFace), OpenCV
- **Frontend:** Streamlit, HTML/JS
- **Tools:** Ngrok, SQLAlchemy, Python-dotenv

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/kasa-maker/ID-and-Face-Detection-System.git
cd ID-and-Face-Detection-System
```

### 2. Create virtual environment
```bash
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Add your Neon DB URL inside .env
```

### 4. Run the project
```bash
# Terminal 1 - API Server
uvicorn main:app --reload

# Terminal 2 - Streamlit UI
streamlit run streamlit_app.py

# Terminal 3 - Ngrok (shareable link)
ngrok http 8000
```

### 5. Extract faces from DB
```bash
python extract_faces.py
```

## 📁 Project Structure
├── main.py              # FastAPI backend
├── database.py          # Database connection
├── models.py            # Database tables
├── schemas.py           # Pydantic schemas
├── extract_faces.py     # Extract faces from DB videos
├── recognize.py         # Live camera recognition
├── streamlit_app.py     # Video upload & recognition UI
├── camera.html          # Employee video registration
└── .env.example         # Environment variables template
## 🔄 How It Works
1. Employee records a short video via `camera.html`
2. Video is stored in Neon Cloud PostgreSQL
3. `extract_faces.py` extracts face images from stored videos
4. Upload a group video in Streamlit — system detects and labels all known employees
5. Download the annotated output video with Name + ID on each face
### 🎥 Live Camera Detection
- Real-time face recognition via webcam
- Detects multiple employees simultaneously in a single frame
- Known employees highlighted with **Green box + Name + ID**
- Unknown persons highlighted with **Red box** and automatically rejected
- Processes every 5th frame for smooth performance — no lag or freezing
- Powered by DeepFace SFace model with cosine similarity matching
```bash
# Run live detection
python recognize.py
## 👤 Author
**Kasaam** — AI Engineering Student 

