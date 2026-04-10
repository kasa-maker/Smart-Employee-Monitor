import streamlit as st
import psycopg2
import pandas as pd
from dotenv import dotenv_values
from datetime import date

# DB Connection
config = dotenv_values(r"C:\Users\LENOVO\Desktop\VIDEO_API\video_api\.env")
DATABASE_URL = config.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def get_attendance():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT name, user_id, 
               check_in, check_out,
               CASE 
                   WHEN check_out IS NOT NULL 
                   THEN ROUND(EXTRACT(EPOCH FROM (check_out - check_in))/3600, 2)
                   ELSE NULL 
               END as hours_worked
        FROM attendance
        WHERE date = CURRENT_DATE
        ORDER BY check_in
    """, conn)
    conn.close()
    return df

def get_mobile_usage():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT name, user_id,
               COUNT(*) as total_times,
               ROUND(SUM(duration_seconds)::numeric/60, 1) as total_minutes
        FROM mobile_usage
        WHERE date = CURRENT_DATE
        GROUP BY name, user_id
        ORDER BY total_minutes DESC
    """, conn)
    conn.close()
    return df

def get_seat_absence():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT name, away_from, away_to,
               ROUND(duration_minutes::numeric, 1) as duration_minutes
        FROM seat_absence
        WHERE date = CURRENT_DATE
        ORDER BY away_from DESC
    """, conn)
    conn.close()
    return df

# ── UI ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Employee Monitoring Dashboard",
    page_icon="👁️",
    layout="wide"
)

st.title("👁️ Employee Monitoring Dashboard")
st.subheader(f"📅 {date.today().strftime('%d %B %Y')}")

st.button("🔄 Refresh")

# ── Attendance ──────────────────────────────────────────
st.markdown("---")
st.markdown("### ✅ Attendance")

attendance = get_attendance()
if attendance.empty:
    st.info("Aaj koi attendance record nahi!")
else:
    # Metrics
    cols = st.columns(4)
    with cols[0]:
        st.metric("Total Present", len(attendance))
    with cols[1]:
        checked_out = attendance['check_out'].notna().sum()
        st.metric("Checked Out", int(checked_out))
    with cols[2]:
        still_in = attendance['check_out'].isna().sum()
        st.metric("Still In Office", int(still_in))
    with cols[3]:
        avg_hours = attendance['hours_worked'].mean()
        st.metric("Avg Hours", f"{avg_hours:.1f}h" if avg_hours else "N/A")

    attendance.columns = ['Name', 'User ID', 'Check In', 'Check Out', 'Hours Worked']
    st.dataframe(attendance, use_container_width=True)

# ── Mobile Usage ────────────────────────────────────────
st.markdown("---")
st.markdown("### 📱 Mobile Usage Today")

mobile = get_mobile_usage()
if mobile.empty:
    st.info("Koi mobile usage record nahi!")
else:
    if not mobile.empty:
        top = mobile.iloc[0]
        st.warning(f"⚠️ Sabse zyada mobile: **{top['name']}** — {top['total_minutes']} minutes")

    cols = st.columns(len(mobile))
    for i, row in mobile.iterrows():
        with cols[i]:
            st.metric(
                label=f"👤 {row['name']}",
                value=f"{row['total_minutes']} min",
                delta=f"{row['total_times']} baar"
            )

    chart_data = mobile.set_index('name')['total_minutes']
    st.bar_chart(chart_data)

# ── Seat Absence ────────────────────────────────────────
st.markdown("---")
st.markdown("### 🪑 Seat Absence (15+ min)")

absence = get_seat_absence()
if absence.empty:
    st.success("✅ Koi bhi 15 min se zyada seat se door nahi gaya!")
else:
    st.error(f"⚠️ {len(absence)} seat absence records aaj!")
    absence.columns = ['Name', 'Away From', 'Away To', 'Duration (min)']
    st.dataframe(absence, use_container_width=True)

# ── Download ────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📥 Download Reports")

col1, col2, col3 = st.columns(3)

with col1:
    if not attendance.empty:
        csv = attendance.to_csv(index=False)
        st.download_button("📥 Attendance CSV", csv,
                          f"attendance_{date.today()}.csv", "text/csv")

with col2:
    if not mobile.empty:
        csv = mobile.to_csv(index=False)
        st.download_button("📥 Mobile Usage CSV", csv,
                          f"mobile_{date.today()}.csv", "text/csv")

with col3:
    if not absence.empty:
        csv = absence.to_csv(index=False)
        st.download_button("📥 Seat Absence CSV", csv,
                          f"absence_{date.today()}.csv", "text/csv")