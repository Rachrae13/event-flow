"""
EVENTFLOW - Smart Venue Conflict Detector View
Detects, visualizes, and advises on concurrent room bookings on the same date.
"""

import streamlit as st
import pandas as pd
from components.data_loader import count_all_venue_conflicts

def render_conflict_view(events_df):
    """Renders the venue collision radar, conflict table, and resolution recommendations."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> VENUE INTELLIGENCE</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Smart Campus Venue Conflict Detector</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Automatically detects overlapping bookings scheduled in the same physical venue on the same date.
        </p>
    </div>
    """, unsafe_allow_html=True)

    conflicts = count_all_venue_conflicts(events_df)
    total_conflicts = len(conflicts)

    c1, c2 = st.columns(2)
    c1.metric("Total Venue Conflicts", total_conflicts)
    c2.metric("Venue Status", "Action Required" if total_conflicts > 0 else "All Venues Clear")

    if total_conflicts > 0:
        st.error(f"🚨 {total_conflicts} venue scheduling conflict(s) detected across campus facilities.")
        
        conflict_df = pd.DataFrame(conflicts).rename(columns={
            "venue": "Venue",
            "date": "Date",
            "event_1_id": "Event 1 ID",
            "event_1_name": "Event 1 Name",
            "event_2_id": "Event 2 ID",
            "event_2_name": "Event 2 Name",
            "conflict_start": "Overlap Starts",
            "conflict_end": "Overlap Ends",
            "duration": "Overlap Duration (min)"
        })
        st.dataframe(conflict_df, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        st.subheader("💡 Conflict Resolution & Alternative Recommendations")
        for c in conflicts:
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom:12px; padding:16px 20px; border-color:rgba(244,63,94,0.35);">
                <div style="font-weight:750; color:#FB7185; font-size:0.98rem; margin-bottom:4px;">
                    ⚠️ Collision at {c['venue']} ({c['conflict_start']} – {c['conflict_end']})
                </div>
                <div style="color:#CBD5E1; font-size:0.85rem; line-height:1.5;">
                    <b>{c['event_1_name']}</b> (#{c['event_1_id']}) overlaps with <b>{c['event_2_name']}</b> (#{c['event_2_id']}) for <b>{c['duration']} minutes</b>.<br>
                    <span style="color:#94A3B8;">Suggested Action: Shift {c['event_2_name']} to start after {c['conflict_end']} or allocate an alternative facility via the <b>Smart Slot Recommendation</b> lab.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No venue conflicts detected. All facility schedules are completely disjoint!")
