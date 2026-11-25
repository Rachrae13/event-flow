"""
EVENTFLOW - Campus Event Explorer View
Provides comprehensive multi-parameter event search, interactive filters,
sorting, and detail inspection panels.
"""

import streamlit as st
import pandas as pd
from components.data_loader import minutes_to_clock

def render_explorer_view(events_df):
    """Renders the Event Explorer interface with live filtering and sorting."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> EVENT INTELLIGENCE</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Campus Event Explorer</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Search, filter, and inspect campus schedules by department, venue, date, and time window.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if events_df.empty:
        st.info("No events found in the database or CSV dataset.")
        return

    # Filter Bar
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        search_query = st.text_input("🔍 Search by Name or ID", placeholder="e.g. Symposium, Lab 1, 3")

    with filter_col2:
        dept_options = ["All Departments"] + sorted(events_df["department"].dropna().unique().tolist())
        selected_dept = st.selectbox("🏢 Department", dept_options)

    with filter_col3:
        venue_options = ["All Venues"] + sorted(events_df["venue"].dropna().unique().tolist())
        selected_venue = st.selectbox("🏛️ Venue", venue_options)

    with filter_col4:
        source_options = ["All Sources", "CSV Seed", "Live SQLite"]
        selected_source = st.selectbox("📦 Data Source", source_options)

    # Time Filter
    t_col1, t_col2, t_col3 = st.columns([1, 1, 2])
    with t_col1:
        filter_start = st.slider("Min Start Hour", 8, 18, 8, format="%02d:00")
    with t_col2:
        filter_end = st.slider("Max End Hour", 9, 20, 18, format="%02d:00")
    with t_col3:
        sort_by = st.selectbox("Sort Events By", ["Start Time (Earliest First)", "Event ID", "Event Name", "Duration"])

    # Apply filters
    filtered_df = events_df.copy()

    if search_query.strip():
        q = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df["event_name"].str.lower().str.contains(q, na=False) |
            filtered_df["event_id"].astype(str).str.contains(q, na=False) |
            filtered_df["venue"].str.lower().str.contains(q, na=False)
        ]

    if selected_dept != "All Departments":
        filtered_df = filtered_df[filtered_df["department"] == selected_dept]

    if selected_venue != "All Venues":
        filtered_df = filtered_df[filtered_df["venue"] == selected_venue]

    if selected_source != "All Sources":
        filtered_df = filtered_df[filtered_df["source"] == selected_source]

    # Time range filter
    min_minutes = filter_start * 60
    max_minutes = filter_end * 60
    filtered_df = filtered_df[
        (filtered_df["start_minutes"] >= min_minutes) &
        (filtered_df["end_minutes"] <= max_minutes)
    ]

    # Sorting
    if sort_by == "Start Time (Earliest First)":
        filtered_df = filtered_df.sort_values(by=["start_minutes", "event_id"])
    elif sort_by == "Event ID":
        filtered_df = filtered_df.sort_values(by="event_id")
    elif sort_by == "Event Name":
        filtered_df = filtered_df.sort_values(by="event_name")
    elif sort_by == "Duration":
        filtered_df = filtered_df.sort_values(by="duration_minutes", ascending=False)

    # Summary bar
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin:14px 0 10px 0;">
        <div style="color:#94A3B8; font-size:0.85rem;">
            Showing <b>{len(filtered_df)}</b> of <b>{len(events_df)}</b> campus events
        </div>
        <div style="display:flex; gap:8px;">
            <span class="neon-pill pill-cyan">Live Results</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Table view
    display_cols = ["event_id", "event_name", "department", "venue", "event_date", "start_time", "end_time", "duration_minutes", "source"]
    st.dataframe(
        filtered_df[display_cols].rename(columns={
            "event_id": "ID",
            "event_name": "Event Name",
            "department": "Department",
            "venue": "Venue",
            "event_date": "Date",
            "start_time": "Start",
            "end_time": "End",
            "duration_minutes": "Duration (min)",
            "source": "Source"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Detail Cards for top results
    if not filtered_df.empty:
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.subheader("🔍 Event Detail Cards")
        cards = filtered_df.head(6)
        cols = st.columns(3)
        for idx, (_, row) in enumerate(cards.iterrows()):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="glass-card" style="margin-bottom:14px; padding:16px 18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="neon-pill pill-cyan">ID #{row['event_id']}</span>
                        <span class="neon-pill {'pill-emerald' if row['source'] == 'Live SQLite' else 'pill-purple'}" style="font-size:0.68rem;">
                            {row['source']}
                        </span>
                    </div>
                    <div style="font-weight:800; font-size:1.05rem; color:#F8FAFC; margin-bottom:4px;">
                        {row['event_name']}
                    </div>
                    <div style="font-size:0.82rem; color:#94A3B8; margin-bottom:10px;">
                        🏢 {row.get('department', 'General')} &nbsp;•&nbsp; 🏛️ {row['venue']}
                    </div>
                    <div style="background:rgba(56,189,248,0.08); padding:8px 12px; border-radius:8px; display:flex; justify-content:space-between; font-size:0.82rem;">
                        <span style="color:#BAE6FD;">🕒 {row['start_time']} – {row['end_time']}</span>
                        <span style="color:#F8FAFC; font-weight:700;">{row['duration_minutes']} min</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
