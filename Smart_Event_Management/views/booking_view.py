"""
EVENTFLOW - Live Campus Event Booking View
Provides the interactive booking form, live SQLite conflict validation,
and database persistence with instant UI updates.
"""

import streamlit as st
import pandas as pd
from event_manager import add_event, check_venue_conflict
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "events.csv"

def render_booking_view(events_df):
    """Renders the live booking form with real-time SQLite conflict checks and persistence."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> LIVE DATABASE BOOKING</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Live Campus Event Booking</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Register new campus events with automated venue conflict checking. All confirmed bookings are committed to SQLite.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_sqlite, tab_csv = st.tabs([
        "🏫 Live SQLite Campus Booking",
        "➕ Add Sample Event to CSV"
    ])

    with tab_sqlite:
        with st.form("form_sqlite_booking"):
            name = st.text_input("Event Name", placeholder="e.g. AI Symposium 2026")
            dept = st.selectbox("Department", [
                "Computer Science", "Artificial Intelligence", "Data Science",
                "Electronics", "Information Tech", "Mechanical", "Civil Engineering",
                "Cyber Security", "Other"
            ])
            venue = st.selectbox("Campus Venue", [
                "Auditorium", "Seminar Hall", "Lab 1", "Lab 2", "Lab 3",
                "Conference Room", "Classroom 1", "Hall A", "Hall B"
            ])
            date = st.date_input("Event Date")

            tc1, tc2 = st.columns(2)
            with tc1:
                start_t = st.time_input("Start Time", value=pd.to_datetime("10:00").time(), key="book_s")
            with tc2:
                end_t = st.time_input("End Time", value=pd.to_datetime("11:30").time(), key="book_e")

            submitted = st.form_submit_button("🚀 Validate & Confirm Booking")

        if submitted:
            start_str = start_t.strftime("%H:%M")
            end_str = end_t.strftime("%H:%M")
            date_str = date.strftime("%Y-%m-%d")

            if not name.strip():
                st.error("Please provide a valid event name.")
            elif start_t >= end_t:
                st.error("End time must be later than start time.")
            else:
                conflicts = check_venue_conflict(venue, date_str, start_str, end_str)
                if conflicts:
                    st.error(f"🚨 Booking Conflict: {venue} is already reserved during this time interval on {date_str}.")
                    st.dataframe(pd.DataFrame(conflicts, columns=["ID", "Conflicting Event", "Start", "End"]), use_container_width=True, hide_index=True)
                else:
                    add_event(name.strip(), dept, venue, date_str, start_str, end_str)
                    st.success(f"🎉 '{name.strip()}' booked successfully in {venue} on {date_str}!")
                    st.rerun()

    with tab_csv:
        st.caption("Appends an entry directly to events.csv for demonstration replay.")
        with st.form("form_csv_addition"):
            csv_name = st.text_input("Sample Event Name", key="csv_n")
            csv_venue = st.text_input("Sample Venue", value="Auditorium", key="csv_v")
            c_s = st.time_input("Start Time", value=pd.to_datetime("09:00").time(), key="csv_s")
            c_e = st.time_input("End Time", value=pd.to_datetime("10:00").time(), key="csv_e")
            csv_submit = st.form_submit_button("Add to CSV")

        if csv_submit:
            if not csv_name.strip():
                st.error("Event name required.")
            elif c_s >= c_e:
                st.error("End time must be after start time.")
            else:
                new_id = int(events_df["event_id"].max()) + 1
                row = pd.DataFrame([{
                    "event_id": new_id,
                    "event_name": csv_name.strip(),
                    "start_time": c_s.strftime("%H:%M"),
                    "end_time": c_e.strftime("%H:%M"),
                    "venue": csv_venue.strip()
                }])
                row.to_csv(CSV_PATH, mode="a", header=False, index=False)
                st.success("Sample event added to events.csv successfully.")
                st.rerun()
