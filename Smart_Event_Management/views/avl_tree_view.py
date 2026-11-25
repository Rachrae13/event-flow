"""
EVENTFLOW - AVL Interval Tree Visualizer View
Provides interactive tree visualization, deep node inspection, insertion replay with
100% reliable callback-driven controls, and real AVL rotation analysis (LL, RR, LR, RL).
"""

import streamlit as st
import pandas as pd
from components.data_loader import get_tree_height, minutes_to_clock
from components.tree_renderer import (
    render_animated_tree,
    get_tree_nodes_and_positions,
    make_insertion_snapshots
)

def render_avl_tree_view(events_df, avl_root):
    """Renders the realistic AVL Interval Tree visualizer with node inspector, replay, and rotation viewer."""
    st.markdown("""
    <div class="hero-banner" style="padding:22px 28px; margin-bottom:18px;">
        <div class="hero-badge"><span class="hero-badge-pulse"></span> DATA STRUCTURE LAB</div>
        <h2 style="margin:2px 0 6px 0; font-size:1.8rem;">Realistic AVL Interval Tree Visualizer</h2>
        <p style="color:#94A3B8; margin:0; font-size:0.9rem;">
            Explore the balanced binary search tree augmented with maximum-end intervals, height balancing, and rotation invariants.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Persistent View Mode Selector (Will never reset or jump tabs unexpectedly)
    if "avl_view_mode" not in st.session_state:
        st.session_state.avl_view_mode = "🌱 Insertion Replay & Rotation Lab"

    selected_view = st.radio(
        "Select AVL Visualizer Mode",
        options=["🌱 Insertion Replay & Rotation Lab", "🔎 Live Tree & Node Inspector"],
        horizontal=True,
        key="avl_view_mode",
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # MODE 1: INSERTION REPLAY & ROTATION LAB
    # =========================================================================
    if selected_view == "🌱 Insertion Replay & Rotation Lab":
        if not events_df.empty:
            snapshots, insertion_order = make_insertion_snapshots(events_df)
            total_snapshots = len(snapshots)

            # Direct widget-bound session state (Single source of truth)
            if "ins_slider" not in st.session_state:
                st.session_state.ins_slider = total_snapshots

            # Ensure valid bounds
            st.session_state.ins_slider = max(1, min(total_snapshots, int(st.session_state.ins_slider)))

            # Callbacks directly modify st.session_state.ins_slider
            def on_prev():
                if st.session_state.ins_slider > 1:
                    st.session_state.ins_slider -= 1

            def on_next():
                if st.session_state.ins_slider < total_snapshots:
                    st.session_state.ins_slider += 1

            def on_reset():
                st.session_state.ins_slider = 1

            # Synchronized Button Controls with on_click callbacks
            c1, c2, c3 = st.columns(3)
            c1.button("◀ Previous Insertion", key="btn_ins_prev", on_click=on_prev)
            c2.button("Next Insertion ▶", key="btn_ins_next", on_click=on_next)
            c3.button("↺ Start Over", key="btn_ins_reset", on_click=on_reset)

            # Slider directly bound to key="ins_slider"
            st.slider(
                "Insertion Sequence Step",
                min_value=1,
                max_value=total_snapshots,
                key="ins_slider"
            )

            current_step = st.session_state.ins_slider
            current_snapshot = snapshots[current_step - 1]
            inserted_ev = current_snapshot["event"]
            tree_at_step = current_snapshot["tree"]
            rotations = current_snapshot["rotations"]

            st.progress(current_step / total_snapshots)

            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.7); border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:12px 18px; margin:12px 0;">
                <span class="neon-pill pill-cyan">Step {current_step} of {total_snapshots}</span> &nbsp;
                <b>Inserted Event:</b> <span style="color:#F8FAFC;">{inserted_ev['event_name']}</span> (ID #{inserted_ev['event_id']}) &nbsp;•&nbsp;
                <b>Interval:</b> <span style="color:#BAE6FD;">{inserted_ev['start_time']} – {inserted_ev['end_time']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Render AVL Tree at this step
            snap_html, snap_height = render_animated_tree(tree_at_step)
            st.components.v1.html(snap_html, height=snap_height, scrolling=True)

            # REAL ROTATION VISUALIZATION
            if rotations:
                st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
                st.subheader("⚡ AVL Balancing Rotation Detected on This Step!")

                for rot in rotations:
                    rot_type = rot["type"]
                    badge_class = "pill-purple" if "L" in rot_type else "pill-cyan"
                    
                    st.markdown(f"""
                    <div class="glass-card" style="border-color: rgba(139, 92, 246, 0.4); background: rgba(30, 20, 50, 0.6); padding: 18px 22px; margin-bottom: 14px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span class="neon-pill {badge_class}" style="font-size:0.85rem;">{rot['type']} ({rot['operation']})</span>
                            <span style="color:#CBD5E1; font-size:0.82rem;">Imbalance at Node: <b>{rot['pivot_name']} (#{rot['pivot_id']})</b> | BF = <b>{rot['balance_factor']:+d}</b></span>
                        </div>
                        <p style="color:#E2E8F0; font-size:0.88rem; line-height:1.5; margin:0 0 12px 0;">
                            {rot['reason']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Before and After Rotation Tree Visualizer
                    st.write("**Before and After Tree Restructuring Comparison:**")
                    comp_tab1, comp_tab2 = st.tabs(["🌳 After Rotation (Balanced State)", "⚠️ Before Rotation (Imbalanced State)"])
                    
                    with comp_tab1:
                        st.caption("Balanced tree after rotation with updated subtree heights and max-end intervals:")
                        aft_html, aft_h = render_animated_tree(rot["after_tree"])
                        st.components.v1.html(aft_html, height=aft_h, scrolling=True)

                    with comp_tab2:
                        st.caption(f"Imbalanced subtree rooted at '{rot['pivot_name']}' before {rot['type']} was executed:")
                        bef_html, bef_h = render_animated_tree(rot["before_tree"])
                        st.components.v1.html(bef_html, height=bef_h, scrolling=True)
            else:
                st.caption("✅ No rotation was required on this step. Tree remains naturally balanced (|BF| ≤ 1).")
        else:
            st.info("No events are available for insertion replay.")

    # =========================================================================
    # MODE 2: LIVE TREE & DEEP NODE INSPECTOR
    # =========================================================================
    else:
        # Legend
        l1, l2, l3, l4 = st.columns(4)
        l1.markdown("🔵 <span style='color:#38BDF8; font-weight:700;'>Unvisited Node</span>", unsafe_allow_html=True)
        l2.markdown("🟢 <span style='color:#34D399; font-weight:700;'>Visited Node</span>", unsafe_allow_html=True)
        l3.markdown("🟡 <span style='color:#00F2FE; font-weight:700;'>Current / Active Node</span>", unsafe_allow_html=True)
        l4.markdown("🔴 <span style='color:#FB7185; font-weight:700;'>Skipped Subtree</span>", unsafe_allow_html=True)

        if avl_root is not None:
            tree_html, tree_height = render_animated_tree(avl_root)
            st.components.v1.html(tree_html, height=tree_height, scrolling=True)

            tree_nodes, _, _, _ = get_tree_nodes_and_positions(avl_root)
            m1, m2, m3 = st.columns(3)
            m1.metric("Tree Nodes", len(tree_nodes))
            m2.metric("Tree Height", get_tree_height(avl_root))
            m3.metric("Root Event", f"{avl_root.event_name} (#{avl_root.event_id})")

            # Node Inspector
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.subheader("🔬 Deep Node Inspector")

            event_options = {
                f"{row['event_name']} (ID: {row['event_id']})": int(row["event_id"])
                for _, row in events_df.iterrows()
            }

            selected_event_label = st.selectbox(
                "Select a node to inspect its internal properties",
                list(event_options.keys()),
                key="avl_inspector_select"
            )
            selected_id = event_options[selected_event_label]

            def find_node(node, event_id):
                if node is None:
                    return None
                if node.event_id == event_id:
                    return node
                found = find_node(node.left, event_id)
                if found is not None:
                    return found
                return find_node(node.right, event_id)

            selected_node = find_node(avl_root, selected_id)

            if selected_node:
                balance = get_tree_height(selected_node.left) - get_tree_height(selected_node.right)
                ic1, ic2, ic3 = st.columns(3)
                ic1.metric("Subtree Height", selected_node.height)
                ic2.metric("Balance Factor (BF)", f"{balance:+d}")
                ic3.metric("Augmented Max End", minutes_to_clock(selected_node.max_end))

                st.markdown(f"""
                <div class="glass-card" style="margin-top:10px; padding:16px 20px;">
                    <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; font-size:0.9rem;">
                        <div><b>Event Name:</b> <span style="color:#F8FAFC;">{selected_node.event_name}</span></div>
                        <div><b>Event ID:</b> <span style="color:#38BDF8;">#{selected_node.event_id}</span></div>
                        <div><b>Time Interval:</b> <span style="color:#BAE6FD;">{minutes_to_clock(selected_node.start)} – {minutes_to_clock(selected_node.end)}</span></div>
                        <div><b>Max End In Subtree:</b> <span style="color:#00F2FE;">{minutes_to_clock(selected_node.max_end)}</span></div>
                        <div><b>Left Child:</b> <span style="color:#94A3B8;">{f'{selected_node.left.event_name} (#{selected_node.left.event_id})' if selected_node.left else 'None'}</span></div>
                        <div><b>Right Child:</b> <span style="color:#94A3B8;">{f'{selected_node.right.event_name} (#{selected_node.right.event_id})' if selected_node.right else 'None'}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No events available in the AVL tree.")
