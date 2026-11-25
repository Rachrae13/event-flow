"""
EVENTFLOW - Advanced Animated Interval Search View
Provides step-by-step interval search animation, tree traversal trace,
color-coded status highlighting, synchronized filter pills, and command center.
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from avl_interval_tree import search_overlaps
from components.data_loader import minutes_to_clock
from components.tree_renderer import render_animated_tree, get_tree_nodes_and_positions, get_node_statuses

def render_interval_search_view(events_df, avl_root):
    """Renders the animated interval search playground with traversal controls, interactive filters, and command center."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> ALGORITHM LAB</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Advanced Animated Interval Search</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Watch the augmented AVL tree evaluate overlapping intervals, prune subtrees based on maximum-end values, and trace decisions step-by-step.
        </p>
    </div>
    """, unsafe_allow_html=True)

    trace_col1, trace_col2 = st.columns(2)
    with trace_col1:
        trace_start = st.time_input("Query Start Time", value=pd.to_datetime("10:00").time(), key="search_lab_start")
    with trace_col2:
        trace_end = st.time_input("Query End Time", value=pd.to_datetime("11:00").time(), key="search_lab_end")

    # Session State Initialization
    if "search_step" not in st.session_state:
        st.session_state.search_step = 1
    if "avl_trace_data" not in st.session_state:
        st.session_state.avl_trace_data = []
    if "avl_match_data" not in st.session_state:
        st.session_state.avl_match_data = []
    if "avl_playing" not in st.session_state:
        st.session_state.avl_playing = False
    if "avl_last_refresh" not in st.session_state:
        st.session_state.avl_last_refresh = -1
    if "avl_filter" not in st.session_state:
        st.session_state.avl_filter = "All"
    if "avl_command_result" not in st.session_state:
        st.session_state.avl_command_result = ""
    if "avl_command_matches" not in st.session_state:
        st.session_state.avl_command_matches = []

    # Auto-initialize on first visit so user immediately sees controls and tree!
    if not st.session_state.avl_trace_data and avl_root is not None:
        init_matches = []
        init_trace = []
        search_overlaps(avl_root, 10 * 60, 11 * 60, init_matches, init_trace)
        st.session_state.avl_trace_data = init_trace
        st.session_state.avl_match_data = [
            {
                "Event ID": int(node.event_id),
                "Event Name": str(node.event_name),
                "Start Time": minutes_to_clock(node.start),
                "End Time": minutes_to_clock(node.end),
                "Max End": minutes_to_clock(node.max_end)
            }
            for node in init_matches
        ]
        st.session_state.search_step = 1

    def run_new_search():
        s_min = trace_start.hour * 60 + trace_start.minute
        e_min = trace_end.hour * 60 + trace_end.minute
        if s_min >= e_min:
            st.error("End time must be later than start time.")
            return

        new_trace = []
        new_matches = []
        search_overlaps(avl_root, s_min, e_min, new_matches, new_trace)

        st.session_state.avl_trace_data = new_trace
        st.session_state.avl_match_data = [
            {
                "Event ID": int(node.event_id),
                "Event Name": str(node.event_name),
                "Start Time": minutes_to_clock(node.start),
                "End Time": minutes_to_clock(node.end),
                "Max End": minutes_to_clock(node.max_end)
            }
            for node in new_matches
        ]
        st.session_state.search_step = 1
        st.session_state.avl_playing = False
        st.session_state.avl_last_refresh = -1
        st.session_state.avl_filter = "All"
        st.session_state.avl_command_result = ""
        st.session_state.avl_command_matches = []
        st.session_state.total_searches = st.session_state.get("total_searches", 0) + 1

    st.button("🚀 Run Interval Search Animation", key="btn_gen_search", on_click=run_new_search, use_container_width=True)

    trace_data = st.session_state.avl_trace_data
    match_data = st.session_state.avl_match_data

    if trace_data:
        total_steps = len(trace_data)
        match_ids = [int(m["Event ID"]) for m in match_data]

        # Direct widget-bound session state (Single source of truth)
        if "trace_slider" not in st.session_state:
            st.session_state.trace_slider = 1

        # Clamp step
        st.session_state.trace_slider = max(1, min(total_steps, int(st.session_state.trace_slider)))

        speed_label = st.select_slider(
            "Animation Speed",
            options=["Slow", "Normal", "Fast"],
            value="Normal",
            key="slider_speed"
        )
        refresh_interval = {"Slow": 1800, "Normal": 1000, "Fast": 450}[speed_label]

        # Callbacks directly modify st.session_state.trace_slider
        def trace_prev():
            st.session_state.avl_playing = False
            if st.session_state.trace_slider > 1:
                st.session_state.trace_slider -= 1

        def trace_play_toggle():
            st.session_state.avl_playing = not st.session_state.avl_playing
            if st.session_state.trace_slider >= total_steps:
                st.session_state.trace_slider = 1

        def trace_next():
            st.session_state.avl_playing = False
            if st.session_state.trace_slider < total_steps:
                st.session_state.trace_slider += 1

        def trace_reset():
            st.session_state.avl_playing = False
            st.session_state.trace_slider = 1
            st.session_state.avl_filter = "All"
            st.session_state.avl_command_result = ""
            st.session_state.avl_command_matches = []

        # Synchronized Navigation Controls with on_click
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
        ctrl1.button("⏮ Previous", key="btn_trace_prev", on_click=trace_prev)
        play_label = "⏸ Pause" if st.session_state.avl_playing else "▶ Play"
        ctrl2.button(play_label, key="btn_trace_play", on_click=trace_play_toggle)
        ctrl3.button("Next ⏭", key="btn_trace_next", on_click=trace_next)
        ctrl4.button("↻ Reset", key="btn_trace_reset", on_click=trace_reset)

        # Autoplay loop handler
        if st.session_state.avl_playing and st.session_state.trace_slider < total_steps:
            rf_count = st_autorefresh(interval=refresh_interval, key="trace_autorefresh")
            if rf_count != st.session_state.avl_last_refresh:
                st.session_state.avl_last_refresh = rf_count
                st.session_state.trace_slider = min(total_steps, st.session_state.trace_slider + 1)
        elif st.session_state.trace_slider >= total_steps:
            st.session_state.avl_playing = False

        # Synchronized Step Slider directly bound to trace_slider
        st.slider(
            "Traversal Step Slider",
            min_value=1,
            max_value=total_steps,
            key="trace_slider"
        )

        cur_step = st.session_state.trace_slider
        cur_row = trace_data[cur_step - 1]
        statuses = get_node_statuses(avl_root, trace_data, cur_step, match_ids)

        st.progress(cur_step / total_steps)

        # Status Metrics
        sm1, sm2, sm3, sm4 = st.columns(4)
        sm1.metric("Current Step", f"{cur_step} / {total_steps}")
        sm2.metric("Visited Nodes", len(statuses["Visited"]))
        sm3.metric("Skipped Subtree Nodes", len(statuses["Skipped"]))
        sm4.metric("Matching Events", len(match_data))

        # =====================================================================
        # INTERACTIVE NODE HIGHLIGHTING FILTERS (Problem A & B)
        # =====================================================================
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        st.subheader("🎨 Node Highlighting Filters")
        st.caption("Click any category below to immediately highlight matching nodes on the tree. Non-selected nodes are softly dimmed.")

        count_all = len(get_tree_nodes_and_positions(avl_root)[0])
        count_unvisited = len(statuses["Unvisited"])
        count_visited = len(statuses["Visited"])
        count_current = len(statuses["Current"])
        count_skipped = len(statuses["Skipped"])
        count_matching = len(match_ids)

        filter_options = [
            ("All", f"🌳 All ({count_all})"),
            ("Unvisited", f"🔵 Unvisited ({count_unvisited})"),
            ("Visited", f"🟢 Visited ({count_visited})"),
            ("Current", f"🟡 Current ({count_current})"),
            ("Skipped", f"🔴 Skipped ({count_skipped})"),
            ("Matching", f"🟣 Matching ({count_matching})")
        ]

        def select_filter(val):
            st.session_state.avl_filter = val

        f_cols = st.columns(6)
        for idx, (f_val, f_lbl) in enumerate(filter_options):
            is_active = (st.session_state.avl_filter == f_val)
            button_label = f"✓ {f_lbl}" if is_active else f_lbl
            f_cols[idx].button(
                button_label,
                key=f"filter_btn_{f_val}",
                on_click=select_filter,
                args=(f_val,),
                use_container_width=True
            )

        active_filter = st.session_state.avl_filter

        # Legend and Active Status Alert
        color_badges = {
            "All": ("pill-cyan", "Showing all nodes in their natural status"),
            "Unvisited": ("pill-cyan", "Highlighting Blue Unvisited nodes"),
            "Visited": ("pill-emerald", "Highlighting Green Visited nodes"),
            "Current": ("pill-amber", "Highlighting Yellow/Cyan Current evaluated node"),
            "Skipped": ("pill-rose", "Highlighting Red Pruned Subtree nodes"),
            "Matching": ("pill-purple", "Highlighting Purple Overlapping Match nodes")
        }
        badge_style, badge_desc = color_badges.get(active_filter, ("pill-cyan", ""))
        st.markdown(f"""
        <div style="margin: 8px 0 14px 0; display:flex; align-items:center; gap:10px;">
            <span class="neon-pill {badge_style}">Active Filter: {active_filter}</span>
            <span style="color:#94A3B8; font-size:0.83rem;">{badge_desc}</span>
        </div>
        """, unsafe_allow_html=True)

        # Render Tree SVG with readable node values
        anim_html, anim_height = render_animated_tree(
            avl_root,
            trace_rows=trace_data,
            current_step=cur_step,
            filter_status=active_filter,
            match_ids=match_ids
        )
        st.components.v1.html(anim_html, height=anim_height, scrolling=True)

        # =====================================================================
        # CURRENT NODE EVALUATION DECISION BOX
        # =====================================================================
        is_visited = cur_row.get("Action") == "Visited"
        is_overlap = int(cur_row.get("ID", -1)) in match_ids
        decision_box_color = "#34D399" if is_visited else "#FB7185"
        action_text = cur_row.get("Action", "Evaluating")

        st.markdown(f"""
        <div class="glass-card" style="padding:16px 20px; border-color:{decision_box_color}; margin-top:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:800; font-size:1.1rem; color:#F8FAFC;">
                    {'🔍 Evaluating Node:' if is_visited else '⏭ Subtree Pruned:'} {cur_row.get('Event')} (Unique ID #{cur_row.get('ID')})
                </div>
                <span class="neon-pill {'pill-emerald' if is_visited else 'pill-rose'}">{action_text}</span>
            </div>
            <div style="margin-top:12px; display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; font-size:0.86rem;">
                <div><b>Node Interval:</b> <span style="color:#BAE6FD;">{minutes_to_clock(cur_row['Start'])} – {minutes_to_clock(cur_row['End'])}</span></div>
                <div><b>Subtree Max End:</b> <span style="color:#00F2FE;">{minutes_to_clock(cur_row['Max End'])}</span></div>
                <div><b>Interval Overlap:</b> <span style="color:{'#C084FC' if is_overlap else '#94A3B8'}; font-weight:750;">{'YES (Match Found!)' if is_overlap else 'No Overlap with Query'}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # =====================================================================
        # NATURAL LANGUAGE COMMAND CENTER
        # =====================================================================
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.subheader("💬 AVL Tree Command Center")
        st.caption("Type commands such as: 'show unvisited nodes', 'show visited nodes', 'show current node', 'show skipped nodes', 'show matching nodes', or 'show all nodes'.")

        with st.form("avl_cmd_form"):
            cmd_text = st.text_input("Enter Command", placeholder="e.g. show matching nodes", key="input_cmd")
            cmd_submit = st.form_submit_button("Execute Command")

        if cmd_submit and cmd_text.strip():
            c = cmd_text.strip().lower()
            cmd_map = {
                "show unvisited nodes": "Unvisited", "show unvisited": "Unvisited", "unvisited nodes": "Unvisited", "unvisited": "Unvisited",
                "show visited nodes": "Visited", "show visited": "Visited", "visited nodes": "Visited", "visited": "Visited",
                "show current node": "Current", "show current": "Current", "current node": "Current", "current": "Current",
                "show skipped nodes": "Skipped", "show skipped": "Skipped", "skipped nodes": "Skipped", "skipped": "Skipped",
                "show matching nodes": "Matching", "show matching": "Matching", "matching nodes": "Matching", "matching": "Matching",
                "show all nodes": "All", "show all": "All", "all nodes": "All", "all": "All"
            }
            target_filter = cmd_map.get(c)
            if target_filter:
                st.session_state.avl_filter = target_filter
                
                # Fetch matching nodes identified strictly by Unique Event ID
                all_tree_nodes, _, _, _ = get_tree_nodes_and_positions(avl_root)
                node_lookup = {int(n["id"]): n for n in all_tree_nodes}

                if target_filter == "All":
                    target_ids = sorted(node_lookup.keys())
                elif target_filter == "Matching":
                    target_ids = sorted(match_ids)
                else:
                    target_ids = sorted(statuses.get(target_filter, set()))

                matched_records = []
                for tid in target_ids:
                    if tid in node_lookup:
                        ninfo = node_lookup[tid]
                        matched_records.append({
                            "Event ID": tid,
                            "Event Name": ninfo["name"],
                            "Interval": f"{minutes_to_clock(ninfo['start'])} – {minutes_to_clock(ninfo['end'])}",
                            "Height": ninfo["height"],
                            "Max End": minutes_to_clock(ninfo["max_end"])
                        })

                st.session_state.avl_command_matches = matched_records
                st.session_state.avl_command_result = f"Command executed: highlighting **{target_filter.lower()}** nodes. Found {len(matched_records)} node(s)."
                st.rerun()
            else:
                st.session_state.avl_command_result = "Unknown command. Supported commands: 'show unvisited nodes', 'show visited nodes', 'show current node', 'show skipped nodes', 'show matching nodes', 'show all nodes'."
                st.session_state.avl_command_matches = []

        if st.session_state.avl_command_result:
            st.info(st.session_state.avl_command_result)
            if st.session_state.avl_command_matches:
                st.dataframe(pd.DataFrame(st.session_state.avl_command_matches), use_container_width=True, hide_index=True)

        # =====================================================================
        # MATCHING EVENTS SUMMARY TABLE
        # =====================================================================
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.subheader("🎯 Final Matching Overlapping Events")
        if match_data:
            st.dataframe(pd.DataFrame(match_data), use_container_width=True, hide_index=True)
        else:
            st.info("No overlapping events found for this interval query.")

        # =====================================================================
        # TRAVERSAL HISTORY
        # =====================================================================
        with st.expander("📜 Full Traversal Trace History", expanded=False):
            hist_df = pd.DataFrame(trace_data[:cur_step])
            for col in ["Start", "End", "Max End"]:
                if col in hist_df.columns:
                    hist_df[col] = hist_df[col].apply(minutes_to_clock)
            st.dataframe(hist_df, use_container_width=True, hide_index=True)
    else:
        st.info("Select a query time interval above and click **Run Interval Search Animation** to run the AVL algorithm.")
