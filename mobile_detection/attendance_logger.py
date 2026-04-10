import psycopg2
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(r"C:\Users\LENOVO\Desktop\VIDEO_API\video_api\.env")
DATABASE_URL = config.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def check_in(user_id, name):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check karo aaj already check-in hua hai?
        cur.execute("""
            SELECT id FROM attendance 
            WHERE user_id = %s AND date = CURRENT_DATE
        """, (user_id,))
        
        existing = cur.fetchone()
        
        if existing:
            print(f"⚠️ {name} aaj pehle se check-in kar chuka hai!")
            cur.close()
            conn.close()
            return False
        
        # Check-in save karo
        cur.execute("""
            INSERT INTO attendance (user_id, name, check_in)
            VALUES (%s, %s, %s)
        """, (user_id, name, datetime.now()))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ {name} check-in ho gaya — {datetime.now().strftime('%I:%M %p')}")
        return True
        
    except Exception as e:
        print(f"❌ Check-in error: {e}")
        return False

def check_out(user_id, name):
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check karo aaj check-in hua tha?
        cur.execute("""
            SELECT id FROM attendance 
            WHERE user_id = %s AND date = CURRENT_DATE
            AND check_out IS NULL
        """, (user_id,))
        
        existing = cur.fetchone()
        
        if not existing:
            print(f"⚠️ {name} ka check-in record nahi mila!")
            cur.close()
            conn.close()
            return False
        
        # Check-out save karo
        cur.execute("""
            UPDATE attendance 
            SET check_out = %s
            WHERE user_id = %s AND date = CURRENT_DATE
            AND check_out IS NULL
        """, (datetime.now(), user_id))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ {name} check-out ho gaya — {datetime.now().strftime('%I:%M %p')}")
        return True
        
    except Exception as e:
        print(f"❌ Check-out error: {e}")
        return False

def log_seat_absence(user_id, name, away_from, away_to):
    duration = (away_to - away_from).total_seconds() / 60
    
    if duration < 15:
        return
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO seat_absence (user_id, name, away_from, away_to, duration_minutes)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, name, away_from, away_to, round(duration, 1)))
        conn.commit()
        cur.close()
        conn.close()
        print(f"⚠️ {name} {round(duration, 1)} min seat se door tha!")
        
    except Exception as e:
        print(f"❌ Seat absence error: {e}")