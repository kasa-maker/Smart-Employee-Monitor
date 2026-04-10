from pydantic import BaseModel

# Ye schema response mein use hoga
class UserVideoResponse(BaseModel):
    id: int
    user_id: str
    name: str
    video_path: str

    class Config:
        from_attributes = True  