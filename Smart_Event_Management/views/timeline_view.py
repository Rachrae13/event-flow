"""
EVENTFLOW - Interactive Campus Event Timeline View
Renders interactive horizontal time distribution, department color-coding,
duration visualizer, and conflict highlighting using Plotly.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from components.theme import get_plotly_dark_theme
from components.data_loader import to_minutes

def sanitize_datetime_str(date_val, time_val):
    """Safely constructs an ISO datetime string without formatting errors."""
    d_str = str(date_val).strip() if (pd.notna(date_val) and str(date_val).strip()) else "2026-11-25"
    t_str = str(time_val).strip() if (pd.notna(time_val) and str(time_val).strip()) else "09:00"
    
    parts = t_str.split(":")
    hours = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 9
    minutes = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return f"{d_str} {hours:02d}:{minutes:02d}:00"

def render_timeline_view(events_df):
    """Renders the interactive Event Timeline using Plotly Gantt-style bars."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> SCHEDULE VISUALIZATION</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Interactive Campus Event Timeline</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Visualize daily event scheduling across campus venues, inspect duration spans, and detect overlapping slots.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if events_df is None or events_df.empty:
        st.info("No campus events currently registered. Book an event using Live Campus Event Booking to populate the timeline.")
        return

    # Filter Bar: Date, Department, Venue
    fc1, fc2, fc3 = st.columns(3)
    
    with fc1:
        date_options = ["All Dates"] + sorted(events_df["event_date"].dropna().astype(str).unique().tolist())
        sel_date = st.selectbox("📅 Filter Date", date_options, key="timeline_date")

    with fc2:
        dept_options = ["All Departments"] + sorted(events_df["department"].dropna().astype(str).unique().tolist())
        sel_dept = st.selectbox("🏢 Filter Department", dept_options, key="timeline_dept")

    with fc3:
        venue_options = ["All Venues"] + sorted(events_df["venue"].dropna().astype(str).unique().tolist())
        sel_venue = st.selectbox("🏛️ Filter Venue", venue_options, key="timeline_venue")

    filtered = events_df.copy()
    if sel_date != "All Dates":
        filtered = filtered[filtered["event_date"].astype(str) == sel_date]
    if sel_dept != "All Departments":
        filtered = filtered[filtered["department"].astype(str) == sel_dept]
    if sel_venue != "All Venues":
        filtered = filtered[filtered["venue"].astype(str) == sel_venue]

    if filtered.empty:
        st.warning("No campus events match the selected filter criteria. Try adjusting the filters.")
        return

    # Construct Plotly Timeline Data
    plot_df = filtered.copy().sort_values(by=["start_minutes", "event_id"], ascending=True)
    
    # Safe Datetime Parsing
    plot_df["start_datetime"] = [
        pd.to_datetime(sanitize_datetime_str(r["event_date"], r["start_time"]))
        for _, r in plot_df.iterrows()
    ]
    plot_df["end_datetime"] = [
        pd.to_datetime(sanitize_datetime_str(r["event_date"], r["end_time"]))
        for _, r in plot_df.iterrows()
    ]
    plot_df["TaskLabel"] = plot_df["event_name"] + " (#" + plot_df["event_id"].astype(str) + ")"

    # Identify Overlapping Events in this view
    overlap_flags = []
    for i, r1 in plot_df.iterrows():
        has_overlap = False
        for j, r2 in plot_df.iterrows():
            if i != j and str(r1["venue"]).strip().lower() == str(r2["venue"]).strip().lower() and str(r1["event_date"]) == str(r2["event_date"]):
                if r1["start_minutes"] < r2["end_minutes"] and r2["start_minutes"] < r1["end_minutes"]:
                    has_overlap = True
                    break
        overlap_flags.append("🚨 Overlapping Conflict" if has_overlap else "Disjoint / Clear")
    plot_df["Schedule Status"] = overlap_flags

    # Build Gantt Timeline
    fig = px.timeline(
        plot_df,
        x_start="start_datetime",
        x_end="end_datetime",
        y="TaskLabel",
        color="department",
        hover_data={
            "TaskLabel": False,
            "venue": True,
            "event_date": True,
            "start_time": True,
            "end_time": True,
            "duration_minutes": True,
            "Schedule Status": True,
            "source": True
        },
        color_discrete_sequence=[
            "#38BDF8", "#8B5CF6", "#00F2FE", "#EC4899", 
            "#10B981", "#F59E0B", "#6366F1", "#14B8A6"
        ]
    )

    # Apply Theme Without Kwarg Collision
    dark_theme = get_plotly_dark_theme()
    layout_params = dict(dark_theme)
    layout_params["height"] = max(380, len(plot_df) * 44 + 110)
    layout_params["yaxis_title"] = "Campus Events"
    layout_params["xaxis_title"] = "Time Schedule"
    layout_params["xaxis"] = dict(
        dark_theme.get("xaxis", {}),
        tickformat="%H:%M",
        gridcolor="rgba(56, 189, 248, 0.12)"
    )
    layout_params["legend"] = dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11, color="#CBD5E1")
    )

    fig.update_layout(**layout_params)
    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Summary Metrics Row
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Timeline Events Displayed", len(plot_df))
    earliest = plot_df.sort_values(by="start_minutes").iloc[0]
    latest = plot_df.sort_values(by="end_minutes", ascending=False).iloc[0]
    sc2.metric("Earliest Start", f"{earliest['start_time']} ({earliest['event_name']})")
    sc3.metric("Latest End", f"{latest['end_time']} ({latest['event_name']})")
