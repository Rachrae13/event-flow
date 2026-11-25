"""
EVENTFLOW - Executive Dashboard View
Renders key metrics, interactive Plotly visualizations, department/venue analytics,
and recent booking activity from real project data.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from components.theme import get_plotly_dark_theme
from components.data_loader import (
    get_tree_height,
    count_all_venue_conflicts,
    minutes_to_clock
)

def render_dashboard_view(events_df, csv_events, db_events, avl_root):
    """Renders the executive dashboard with animated metric cards and charts."""

    total_events = len(events_df)
    live_count = len(db_events)
    venue_count = events_df["venue"].nunique() if not events_df.empty else 0
    tree_height = get_tree_height(avl_root)
    conflicts = count_all_venue_conflicts(events_df)
    total_conflicts = len(conflicts)

    # Track interval searches in session state
    if "total_searches" not in st.session_state:
        st.session_state.total_searches = 0

    # =========================================================================
    # 1. HERO & WELCOME BANNER
    # =========================================================================
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-badge">
            <span class="hero-badge-pulse"></span>
            EVENTFLOW CORE v2.5 · AVL ENGINE ACTIVE
        </div>
        <h1 class="hero-title">Campus Event & Interval Intelligence</h1>
        <p class="hero-subtitle">
            Real-time campus event scheduling, high-performance interval querying powered by 
            augmented AVL trees, live SQLite conflict resolution, and venue optimization.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Presentation Download Action Banner
    from pathlib import Path
    pptx_path = Path(__file__).resolve().parent.parent / "EVENTFLOW_Project_Presentation.pptx"
    if pptx_path.exists():
        with open(pptx_path, "rb") as f:
            pptx_data = f.read()
        p_c1, p_c2 = st.columns([3, 1])
        with p_c1:
            st.markdown("""
            <div style="background: rgba(15, 26, 48, 0.75); border: 1px solid rgba(0, 242, 254, 0.28); border-radius: 12px; padding: 10px 16px; margin-bottom: 14px;">
                <span style="font-size: 0.8rem; font-weight: 750; color: #00F2FE; text-transform: uppercase; letter-spacing: 0.05em;">🎓 Project Presentation Deck Ready</span><br>
                <span style="font-size: 0.85rem; color: #CBD5E1;">16 Widescreen Slides covering Abstract, Problem Statement, AVL Pruning, Benchmark Latency & Comparison Matrix.</span>
            </div>
            """, unsafe_allow_html=True)
        with p_c2:
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download PPT (.pptx)",
                data=pptx_data,
                file_name="EVENTFLOW_Project_Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )

    # =========================================================================
    # 2. KEY METRICS (6 KPI CARDS)
    # =========================================================================
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-icon-wrap" style="color: #38BDF8;">📅</div>
            <div class="metric-title">Total Events</div>
            <div class="metric-val">{total_events}</div>
            <div class="metric-sub"><span style="color:#38BDF8;">●</span> Unified Records</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-icon-wrap" style="color: #34D399;">💾</div>
            <div class="metric-title">Live Bookings</div>
            <div class="metric-val" style="color: #34D399;">{live_count}</div>
            <div class="metric-sub"><span style="color:#34D399;">●</span> SQLite Database</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-icon-wrap" style="color: #A78BFA;">🏛️</div>
            <div class="metric-title">Active Venues</div>
            <div class="metric-val">{venue_count}</div>
            <div class="metric-sub"><span style="color:#A78BFA;">●</span> Campus Facilities</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        conflict_color = "#FB7185" if total_conflicts > 0 else "#34D399"
        conflict_status = "Conflicts Detected" if total_conflicts > 0 else "Schedule Clean"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-icon-wrap" style="color: {conflict_color};">🚨</div>
            <div class="metric-title">Venue Conflicts</div>
            <div class="metric-val" style="color: {conflict_color};">{total_conflicts}</div>
            <div class="metric-sub"><span style="color:{conflict_color};">●</span> {conflict_status}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-icon-wrap" style="color: #00F2FE;">🌳</div>
            <div class="metric-title">AVL Tree Height</div>
            <div class="metric-val" style="color: #00F2FE;">{tree_height}</div>
            <div class="metric-sub"><span style="color:#00F2FE;">●</span> O(log n) Balanced</div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-icon-wrap" style="color: #FBBF24;">⚡</div>
            <div class="metric-title">Interval Searches</div>
            <div class="metric-val" style="color: #FBBF24;">{st.session_state.total_searches}</div>
            <div class="metric-sub"><span style="color:#FBBF24;">●</span> Query Lab Usage</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # 3. INTERACTIVE ANALYTICS CHARTS (Plotly)
    # =========================================================================
    chart_col1, chart_col2 = st.columns([1, 1])

    dark_theme = get_plotly_dark_theme()

    with chart_col1:
        st.markdown("""
        <div class="section-head">
            <div class="section-head-title">🏢 Department-wise Distribution</div>
            <span class="neon-pill pill-purple">Real Dataset Breakdown</span>
        </div>
        """, unsafe_allow_html=True)

        if not events_df.empty and "department" in events_df.columns:
            dept_counts = events_df["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Events"]

            fig_dept = px.pie(
                dept_counts,
                values="Events",
                names="Department",
                hole=0.62,
                color_discrete_sequence=[
                    "#38BDF8", "#8B5CF6", "#00F2FE", "#EC4899", 
                    "#10B981", "#F59E0B", "#6366F1", "#94A3B8"
                ]
            )
            fig_dept.update_layout(
                **dark_theme,
                height=310,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.02,
                    font=dict(size=11, color="#CBD5E1")
                ),
                annotations=[{
                    "text": f"<b>{total_events}</b><br><span style='font-size:10px;color:#94A3B8'>EVENTS</span>",
                    "showarrow": False,
                    "font": {"size": 17, "color": "#F8FAFC"}
                }]
            )
            fig_dept.update_traces(
                textposition="inside",
                textinfo="percent",
                marker=dict(line=dict(color="#060A14", width=2))
            )
            st.plotly_chart(fig_dept, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No department data available.")

    with chart_col2:
        st.markdown("""
        <div class="section-head">
            <div class="section-head-title">🏛️ Venue Booking Frequency</div>
            <span class="neon-pill pill-cyan">Facility Utilization</span>
        </div>
        """, unsafe_allow_html=True)

        if not events_df.empty and "venue" in events_df.columns:
            venue_counts = events_df["venue"].value_counts().reset_index()
            venue_counts.columns = ["Venue", "Bookings"]
            venue_counts = venue_counts.sort_values(by="Bookings", ascending=True)

            fig_venue = px.bar(
                venue_counts,
                x="Bookings",
                y="Venue",
                orientation="h",
                color="Bookings",
                color_continuous_scale=[
                    [0.0, "rgba(56, 189, 248, 0.4)"],
                    [1.0, "rgba(0, 242, 254, 0.95)"]
                ]
            )
            fig_venue.update_layout(
                **dark_theme,
                height=310,
                coloraxis_showscale=False,
                xaxis_title="Number of Booked Events",
                yaxis_title=""
            )
            fig_venue.update_traces(
                marker=dict(
                    line=dict(color="rgba(0, 242, 254, 0.6)", width=1.2),
                    cornerradius=6
                )
            )
            st.plotly_chart(fig_venue, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No venue booking data available.")

    # =========================================================================
    # 4. HOURLY SCHEDULE DENSITY & CONFLICT RADAR
    # =========================================================================
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    time_col1, time_col2 = st.columns([1.4, 1])

    with time_col1:
        st.markdown("""
        <div class="section-head">
            <div class="section-head-title">⏱️ Campus Schedule Density by Hour</div>
            <span class="neon-pill pill-emerald">09:00 — 17:00 Daily Matrix</span>
        </div>
        """, unsafe_allow_html=True)

        # Calculate concurrency per hour
        hours = list(range(9, 18))
        concurrency = []
        for h in hours:
            slot_start = h * 60
            slot_end = (h + 1) * 60
            # Count overlapping events
            count = 0
            for _, ev in events_df.iterrows():
                if ev["start_minutes"] < slot_end and slot_start < ev["end_minutes"]:
                    count += 1
            concurrency.append(count)

        density_df = pd.DataFrame({
            "Time": [f"{h:02d}:00" for h in hours],
            "Active Events": concurrency
        })

        fig_density = go.Figure()
        fig_density.add_trace(go.Scatter(
            x=density_df["Time"],
            y=density_df["Active Events"],
            mode="lines+markers",
            fill="tozeroy",
            line=dict(color="#38BDF8", width=3),
            fillcolor="rgba(56, 189, 248, 0.12)",
            marker=dict(size=8, color="#00F2FE", line=dict(color="#FFFFFF", width=1.5)),
            name="Concurrent Events"
        ))
        fig_density.update_layout(
            **dark_theme,
            height=250,
            xaxis_title="Campus Hour",
            yaxis_title="Concurrent Events",
            showlegend=False
        )
        st.plotly_chart(fig_density, use_container_width=True, config={"displayModeBar": False})

    with time_col2:
        st.markdown("""
        <div class="section-head">
            <div class="section-head-title">🛡️ Schedule Health Radar</div>
            <span class="neon-pill pill-amber">Integrity Status</span>
        </div>
        """, unsafe_allow_html=True)

        if total_conflicts > 0:
            st.markdown(f"""
            <div class="glass-card" style="border-color: rgba(244, 63, 94, 0.4); background: rgba(50, 15, 25, 0.6);">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                    <span style="font-size:1.6rem;">🚨</span>
                    <div>
                        <div style="color:#FB7185; font-weight:800; font-size:1rem;">{total_conflicts} Conflict(s) Detected</div>
                        <div style="color:#94A3B8; font-size:0.8rem;">Action needed on shared venue slots</div>
                    </div>
                </div>
                <p style="color:#CBD5E1; font-size:0.84rem; line-height:1.4; margin:0 0 12px 0;">
                    Double-bookings exist on the same date and facility. Use the <b>Venue Conflict Detector</b> to inspect overlapping intervals and resolve them.
                </p>
                <div style="font-size:0.78rem; color:#FB7185; font-weight:700;">
                    First Conflict: {conflicts[0]['venue']} ({conflicts[0]['conflict_start']}–{conflicts[0]['conflict_end']})
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="border-color: rgba(16, 189, 129, 0.4); background: rgba(10, 40, 25, 0.5);">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                    <span style="font-size:1.6rem;">✅</span>
                    <div>
                        <div style="color:#34D399; font-weight:800; font-size:1rem;">Zero Scheduling Conflicts</div>
                        <div style="color:#94A3B8; font-size:0.8rem;">All venue bookings are strictly disjoint</div>
                    </div>
                </div>
                <p style="color:#CBD5E1; font-size:0.84rem; line-height:1.4; margin:0;">
                    Every campus facility has valid non-overlapping intervals. All interval search queries operate with optimal AVL subtree pruning.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Algorithmic Guarantee Pill
        st.markdown(f"""
        <div style="margin-top:14px; padding:12px 14px; border-radius:12px; background:rgba(15,23,42,0.6); border:1px solid rgba(56,189,248,0.12); font-size:0.82rem; color:#94A3B8;">
            <div style="color:#F8FAFC; font-weight:700; margin-bottom:3px;">🌳 AVL Balancing Invariant</div>
            Max theoretical height for {total_events} nodes: <b>≤ {int(1.44 * (total_events + 2).bit_length()) + 1}</b><br>
            Current actual height: <b style="color:#00F2FE;">{tree_height}</b> (strictly balanced)
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # 5. RECENT ACTIVITY & UPCOMING EVENTS FEED
    # =========================================================================
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    act_col1, act_col2 = st.columns([1, 1])

    with act_col1:
        st.markdown("""
        <div class="section-head">
            <div class="section-head-title">📋 Campus Events Feed</div>
            <span class="neon-pill pill-cyan">All Registered Events</span>
        </div>
        """, unsafe_allow_html=True)

        # Show first 5 events
        display_events = events_df.sort_values(by=["start_minutes", "event_id"]).head(5)
        for _, row in display_events.iterrows():
            source_color = "#34D399" if row["source"] == "Live SQLite" else "#38BDF8"
            st.markdown(f"""
            <div class="activity-row">
                <div class="activity-info">
                    <div class="activity-avatar" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8;">
                        #{row['event_id']}
                    </div>
                    <div>
                        <div class="activity-name">{row['event_name']}</div>
                        <div class="activity-meta">
                            🏛️ {row['venue']} &nbsp;•&nbsp; 🏢 {row.get('department', 'Campus')}
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight:750; color:#F8FAFC; font-size:0.88rem;">{row['start_time']} – {row['end_time']}</div>
                    <span class="neon-pill" style="background:rgba(56,189,248,0.1); color:{source_color}; font-size:0.68rem;">
                        {row['source']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with act_col2:
        st.markdown("""
        <div class="section-head">
            <div class="section-head-title">⚡ Quick System Actions</div>
            <span class="neon-pill pill-purple">Fast Navigation</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card" style="padding:18px 20px;">
            <div style="color:#F8FAFC; font-weight:750; margin-bottom:8px; font-size:0.95rem;">
                Explore Core System Capabilities:
            </div>
            <p style="color:#94A3B8; font-size:0.83rem; margin-bottom:16px;">
                Switch between sections via the sidebar to visualize AVL rotations, run animated interval queries, explore the department timeline, or register new events.
            </p>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <div style="padding:10px 14px; border-radius:10px; background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.16); display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.85rem; color:#E2E8F0; font-weight:600;">🌳 AVL Tree Visualizer</span>
                    <span style="font-size:0.75rem; color:#38BDF8;">Real Nodes & Rotations</span>
                </div>
                <div style="padding:10px 14px; border-radius:10px; background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.16); display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.85rem; color:#E2E8F0; font-weight:600;">🔍 Interval Search Lab</span>
                    <span style="font-size:0.75rem; color:#C084FC;">Subtree Pruning Trace</span>
                </div>
                <div style="padding:10px 14px; border-radius:10px; background:rgba(16,189,129,0.08); border:1px solid rgba(16,189,129,0.16); display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.85rem; color:#E2E8F0; font-weight:600;">🏫 Live Campus Booking</span>
                    <span style="font-size:0.75rem; color:#34D399;">Instant Conflict Check</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
