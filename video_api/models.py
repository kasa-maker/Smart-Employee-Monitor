from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base

class UserVideo(Base):
    __tablename__ = "user_videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    name = Column(String)
    video_data = Column(LargeBinary)  # video bytes save ho rahe hain