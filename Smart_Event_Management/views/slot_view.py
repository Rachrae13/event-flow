"""
EVENTFLOW - Smart Venue Slot Recommendation View
Finds available time windows for venues between 09:00 and 17:00,
merging existing intervals and computing disjoint free slots.
"""

import streamlit as st
import pandas as pd
from components.data_loader import to_minutes, minutes_to_clock

def render_slot_view(events_df):
    """Renders the venue availability calculator and slot recommendation matrix."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> SMART SCHEDULER</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Smart Venue Slot Recommendation</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Find optimal, non-overlapping free time windows for any campus venue and date.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        venues = [
            "Auditorium", "Seminar Hall", "Lab 1", "Lab 2", "Lab 3",
            "Conference Room", "Classroom 1", "Hall A", "Hall B"
        ]
        sel_venue = st.selectbox("Select Target Facility", venues, key="rec_venue")
    with col2:
        sel_date = st.date_input("Select Event Date", key="rec_date")

    req_duration = st.select_slider(
        "Required Event Duration (Minutes)",
        options=[30, 45, 60, 90, 120, 150, 180],
        value=60,
        format_func=lambda val: f"{val} min"
    )

    if st.button("✨ Discover Available Time Slots", key="btn_find_slots"):
        date_str = sel_date.strftime("%Y-%m-%d")

        # Filter events for this venue and date
        venue_events = events_df[
            (events_df["venue"].astype(str).str.strip().str.lower() == sel_venue.strip().lower()) &
            (events_df["event_date"].astype(str) == date_str)
        ].copy()

        working_start = 9 * 60
        working_end = 17 * 60

        occupied = []
        for _, ev in venue_events.iterrows():
            s = max(to_minutes(ev["start_time"]), working_start)
            e = min(to_minutes(ev["end_time"]), working_end)
            if s < e:
                occupied.append((s, e))

        occupied.sort()
        merged = []
        for s, e in occupied:
            if not merged or s > merged[-1][1]:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)

        available = []
        current = working_start
        for s, e in merged:
            if s - current >= req_duration:
                available.append({
                    "Available Start": minutes_to_clock(current),
                    "Available End": minutes_to_clock(s),
                    "Free Duration": f"{s - current} minutes"
                })
            current = max(current, e)

        if working_end - current >= req_duration:
            available.append({
                "Available Start": minutes_to_clock(current),
                "Available End": minutes_to_clock(working_end),
                "Free Duration": f"{working_end - current} minutes"
            })

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.subheader(f"Availability for {sel_venue} on {date_str}")

        if available:
            st.success(f"🎯 {len(available)} suitable free window(s) of at least {req_duration} min found.")
            st.dataframe(pd.DataFrame(available), use_container_width=True, hide_index=True)
        else:
            st.warning(f"No continuous slot of {req_duration} minutes available between 09:00 and 17:00.")

        if not venue_events.empty:
            st.caption("Existing bookings on this date:")
            st.dataframe(venue_events[["event_name", "start_time", "end_time", "source"]], use_container_width=True, hide_index=True)
        else:
            st.info("Facility has 0 existing bookings on this date. Full 09:00–17:00 window available.")
