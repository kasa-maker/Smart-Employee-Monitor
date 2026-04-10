import psycopg2
from datetime import datetime
import os
from dotenv import dotenv_values

# .env file from video_api folder
config = dotenv_values(r"C:\Users\LENOVO\Desktop\VIDEO_API\video_api\.env")
DATABASE_URL = config.get("DATABASE_URL")

def log_mobile_usage(user_id, name, start_time, end_time):
    duration = (end_time - start_time).total_seconds()
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO mobile_usage (user_id, name, start_time, end_time, duration_seconds)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, name, start_time, end_time, duration))
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ DB mein save ho gaya — {name} ne {duration:.1f} sec mobile use kiya")
    except Exception as e:
        print(f"❌ DB error: {e}")