from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session
from moviepy import VideoFileClip
import shutil, os

from database import engine, get_db, Base
from models import UserVideo
from fastapi.staticfiles import StaticFiles


Base.metadata.create_all(bind=engine)

app = FastAPI()
os.makedirs("uploaded_videos", exist_ok=True)
app.mount("/videos", StaticFiles(directory="uploaded_videos"), name="videos")

@app.get("/")
def serve_ui():
    return FileResponse("camera.html")

UPLOAD_DIR = "uploaded_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
@app.get("/videos")
def get_all_videos(db: Session = Depends(get_db)):
    videos = db.query(UserVideo).all()
    return videos
@app.post("/upload")
async def upload_video(
    name: str = Form(...),
    user_id: str = Form(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Video bytes mein read karo
    video_bytes = await video.read()

    # Duration check ke liye temp file
    temp_path = f"temp_{video.filename}"
    with open(temp_path, "wb") as f:
        f.write(video_bytes)

    clip = VideoFileClip(temp_path)
    duration = clip.duration
    clip.close()
    os.remove(temp_path)  # temp file delete

    if duration > 10:
        raise HTTPException(
            status_code=400,
            detail=f"Video bohot lambi hai! Max 10 sec, tumhari {duration:.1f} sec"
        )

    # Seedha DB mein save karo
    record = UserVideo(
        user_id=user_id,
        name=name,
        video_data=video_bytes  # bytes save ho rahe hain
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Video successfully save ho gayi!",
        "id": record.id,
        "name": record.name,
        "user_id": record.user_id
    }

@app.get("/video/{user_id}")
def get_video(user_id: str, db: Session = Depends(get_db)):
    record = db.query(UserVideo).filter(UserVideo.user_id == user_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Video nahi mili!")
    
    return Response(
        content=record.video_data,
        media_type="video/mp4"
    )