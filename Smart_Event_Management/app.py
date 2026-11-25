"""
EVENTFLOW – Smart Event and Interval Query Management System Using AVL Interval Trees
Master Application Orchestrator & Multi-View Navigation Hub
"""

import sys
import streamlit as st

# Automatic Streamlit Launcher: Allows running directly with Python or VS Code Play button
if not st.runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", sys.argv[0]]
    sys.exit(stcli.main())

from pathlib import Path

# Core Data Structure & Backend Imports
from avl_interval_tree import Node, insert, search_overlaps
from event_manager import add_event, get_all_events, check_venue_conflict

# Components & Data Layer
from components.theme import apply_custom_theme
from components.data_loader import load_unified_events, get_tree_height, count_all_venue_conflicts

# Modular Views
from views.dashboard_view import render_dashboard_view
from views.explorer_view import render_explorer_view
from views.avl_tree_view import render_avl_tree_view
from views.interval_search_view import render_interval_search_view
from views.timeline_view import render_timeline_view
from views.conflict_view import render_conflict_view
from views.slot_view import render_slot_view
from views.performance_view import render_performance_view
from views.booking_view import render_booking_view

# =========================================================================
# 1. PAGE CONFIGURATION
# =========================================================================
st.set_page_config(
    page_title="EVENTFLOW | Smart Campus Management",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Futuristic Cyber Theme
apply_custom_theme()

# =========================================================================
# 2. DATA LOAD & AVL TREE CONSTRUCTION
# =========================================================================
events_df, csv_events, db_events, avl_root = load_unified_events()
total_events = len(events_df)
live_count = len(db_events)
tree_height = get_tree_height(avl_root)
conflicts = count_all_venue_conflicts(events_df)
total_conflicts = len(conflicts)

# =========================================================================
# 3. SIDEBAR NAVIGATION & SYSTEM TELEMETRY
# =========================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(56, 189, 248, 0.16); margin-bottom: 18px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #00F2FE, #6366F1); display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">
                🌳
            </div>
            <div>
                <div style="font-size: 1.25rem; font-weight: 850; letter-spacing: -0.02em; background: linear-gradient(135deg, #FFFFFF, #38BDF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    EVENTFLOW
                </div>
                <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; letter-spacing: 0.05em;">
                    AVL INTERVAL TREE ENGINE
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_selection = st.radio(
        "Navigation",
        [
            "🏠 Executive Dashboard",
            "📋 Campus Event Explorer",
            "🌳 AVL Interval Tree Visualizer",
            "🔍 Animated Interval Search",
            "📅 Interactive Event Timeline",
            "🚨 Smart Venue Conflict Detector",
            "🕒 Smart Slot Recommendation",
            "⚡ Performance Analysis Lab",
            "🏫 Live Campus Event Booking"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 📥 Official Project Presentation Download Button
    pptx_file_path = Path(__file__).resolve().parent / "EVENTFLOW_Project_Presentation.pptx"
    if pptx_file_path.exists():
        with open(pptx_file_path, "rb") as f:
            pptx_bytes = f.read()
        st.download_button(
            label="📥 Download Presentation (.pptx)",
            data=pptx_bytes,
            file_name="EVENTFLOW_Project_Presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Sidebar Quick Telemetry Box
    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(56, 189, 248, 0.12); border-radius: 14px; padding: 14px 16px;">
        <div style="font-size: 0.75rem; color: #38BDF8; font-weight: 750; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">
            System Telemetry
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 6px;">
            <span style="color: #94A3B8;">Total Events</span>
            <span style="color: #F8FAFC; font-weight: 700;">{total_events}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 6px;">
            <span style="color: #94A3B8;">Live Bookings</span>
            <span style="color: #34D399; font-weight: 700;">{live_count}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 6px;">
            <span style="color: #94A3B8;">AVL Tree Height</span>
            <span style="color: #00F2FE; font-weight: 700;">{tree_height}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem;">
            <span style="color: #94A3B8;">Conflicts</span>
            <span style="color: {'#FB7185' if total_conflicts > 0 else '#34D399'}; font-weight: 700;">{total_conflicts}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: 20px; text-align: center; font-size: 0.72rem; color: #64748B;">
        EVENTFLOW v2.5<br>M.Tech DSA Project Evaluation
    </div>
    """, unsafe_allow_html=True)

# =========================================================================
# 4. VIEW ROUTER
# =========================================================================
if "Dashboard" in nav_selection:
    render_dashboard_view(events_df, csv_events, db_events, avl_root)
elif "Explorer" in nav_selection:
    render_explorer_view(events_df)
elif "Visualizer" in nav_selection:
    render_avl_tree_view(events_df, avl_root)
elif "Interval Search" in nav_selection:
    render_interval_search_view(events_df, avl_root)
elif "Timeline" in nav_selection:
    render_timeline_view(events_df)
elif "Conflict Detector" in nav_selection:
    render_conflict_view(events_df)
elif "Slot Recommendation" in nav_selection:
    render_slot_view(events_df)
elif "Performance" in nav_selection:
    render_performance_view(events_df, avl_root)
elif "Booking" in nav_selection:
    render_booking_view(events_df)

# =========================================================================
# 5. GLOBAL FOOTER
# =========================================================================
st.markdown("""
<div style="margin-top: 45px; padding-top: 18px; border-top: 1px solid rgba(56, 189, 248, 0.12); text-align: center; color: #64748B; font-size: 0.8rem;">
    EVENTFLOW · Smart Event & Interval Query Management System Using Augmented AVL Trees<br>
    <span style="color: #94A3B8; font-size: 0.75rem;">Powered by Python, Streamlit, SQLite & Plotly</span>
</div>
""", unsafe_allow_html=True)
