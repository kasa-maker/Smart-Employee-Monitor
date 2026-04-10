import streamlit as st
import psycopg2
import pandas as pd
from dotenv import dotenv_values
from datetime import datetime, date

# DB Connection
config = dotenv_values(r"C:\Users\LENOVO\Desktop\VIDEO_API\video_api\.env")
DATABASE_URL = config.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def get_today_data():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT name, user_id, 
               start_time, end_time, 
               ROUND(duration_seconds::numeric, 1) as duration_seconds
        FROM mobile_usage
        WHERE date = CURRENT_DATE
        ORDER BY start_time DESC
    """, conn)
    conn.close()
    return df

def get_summary():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT name, user_id,
               COUNT(*) as total_times,
               ROUND(SUM(duration_seconds)::numeric, 1) as total_seconds,
               ROUND(AVG(duration_seconds)::numeric, 1) as avg_seconds
        FROM mobile_usage
        WHERE date = CURRENT_DATE
        GROUP BY name, user_id
        ORDER BY total_seconds DESC
    """, conn)
    conn.close()
    return df

# ── UI ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Mobile Usage Dashboard",
    page_icon="📱",
    layout="wide"
)

st.title("📱 Mobile Usage Dashboard")
st.subheader(f"📅 Aaj ki Report — {date.today().strftime('%d %B %Y')}")

# Auto refresh
st.button("🔄 Refresh")

# ── Summary Cards ──
st.markdown("---")
summary = get_summary()

if summary.empty:
    st.info("Aaj abhi koi mobile usage record nahi hai!")
else:
    st.markdown("### 👥 Employee Summary")
    cols = st.columns(len(summary))
    
    for i, row in summary.iterrows():
        with cols[i]:
            mins = round(row['total_seconds'] / 60, 1)
            st.metric(
                label=f"👤 {row['name']}",
                value=f"{mins} min",
                delta=f"{row['total_times']} baar use kiya"
            )

    # ── Top User Warning ──
    st.markdown("---")
    top_user = summary.iloc[0]
    top_mins = round(top_user['total_seconds'] / 60, 1)
    st.warning(f"⚠️ Sabse zyada mobile use: **{top_user['name']}** — {top_mins} minutes aaj!")

    # ── Bar Chart ──
    st.markdown("### 📊 Mobile Usage Chart (Minutes)")
    chart_data = summary[['name', 'total_seconds']].copy()
    chart_data['minutes'] = (chart_data['total_seconds'] / 60).round(2)
    chart_data = chart_data.set_index('name')
    st.bar_chart(chart_data['minutes'])

# ── Detailed Log ──
st.markdown("---")
st.markdown("### 📋 Detailed Log")
today_data = get_today_data()

if today_data.empty:
    st.info("Koi record nahi!")
else:
    today_data.columns = ['Name', 'User ID', 'Start Time', 'End Time', 'Duration (sec)']
    st.dataframe(today_data, use_container_width=True)

    # Download button
    csv = today_data.to_csv(index=False)
    st.download_button(
        label="📥 CSV Download karo",
        data=csv,
        file_name=f"mobile_usage_{date.today()}.csv",
        mime="text/csv"
    )