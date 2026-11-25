"""
Unit test suite verifying all fixes for EVENTFLOW Issues 1, 2, and 3.
"""

from components.data_loader import load_unified_events
from components.tree_renderer import (
    make_insertion_snapshots,
    render_animated_tree,
    get_tree_nodes_and_positions,
    get_node_statuses
)
from avl_interval_tree import search_overlaps
from views.timeline_view import sanitize_datetime_str
import pandas as pd
import plotly.express as px

print("--- 1. Testing Data Loading ---")
df, csv_df, db_df, root = load_unified_events()
print(f"Loaded {len(df)} total events ({len(csv_df)} CSV, {len(db_df)} SQLite).")
assert len(df) > 0
assert root is not None

print("\n--- 2. Testing AVL Tree Replay & Rotation Tracking (Issue 1) ---")
snapshots, order = make_insertion_snapshots(df)
print(f"Total insertion snapshots: {len(snapshots)}")
assert len(snapshots) == len(df)

rotations_found = [s for s in snapshots if s["rotations"]]
print(f"Snapshots triggering real AVL rotations: {len(rotations_found)}")
for s in rotations_found:
    rot = s["rotations"][0]
    print(f"  -> Step {s['step']}: {rot['type']} ({rot['operation']}) on pivot '{rot['pivot_name']}' (#{rot['pivot_id']}) with BF = {rot['balance_factor']:+d}")
assert len(rotations_found) > 0, "Expected rotations to be recorded during tree construction"

print("\n--- 3. Testing Tree Node Card Attributes (Issues 1B & 2B) ---")
html_doc, svg_height = render_animated_tree(root)
assert "node-name" in html_doc, "Missing node-name"
assert "node-id" in html_doc, "Missing node-id"
assert "node-interval" in html_doc, "Missing node-interval"
assert "node-meta" in html_doc, "Missing node-meta (Height & BF)"
assert "node-max-end" in html_doc, "Missing node-max-end"
print(f"Node SVG generated cleanly with height {svg_height}px. All 5 node data lines verified!")

print("\n--- 4. Testing Animated Interval Search & Filters (Issue 2) ---")
trace = []
matches = []
search_overlaps(root, 10 * 60, 11 * 60, matches, trace)
match_ids = [m.event_id for m in matches]
print(f"Interval search [10:00 - 11:00]: found {len(matches)} matching events across {len(trace)} traversal steps.")
assert len(matches) > 0
assert len(trace) > 0

statuses = get_node_statuses(root, trace, len(trace), match_ids)
print(f"Statuses at final step -> Visited: {len(statuses['Visited'])}, Skipped: {len(statuses['Skipped'])}, Current: {len(statuses['Current'])}, Matching: {len(statuses['Matching'])}, Unvisited: {len(statuses['Unvisited'])}")
assert len(statuses["Visited"]) > 0
assert len(statuses["Matching"]) == len(matches)

for filter_mode in ["All", "Unvisited", "Visited", "Current", "Skipped", "Matching"]:
    filtered_html, _ = render_animated_tree(root, trace, len(trace), filter_status=filter_mode, match_ids=match_ids)
    assert "node-dimmed" in filtered_html if filter_mode != "All" else True
    print(f"  Filter '{filter_mode}' rendered successfully.")

print("\n--- 5. Testing Interactive Event Timeline (Issue 3) ---")
sanitized_dt = sanitize_datetime_str("2026-11-25", "10:30")
assert sanitized_dt == "2026-11-25 10:30:00"

plot_df = df.copy()
plot_df["start_datetime"] = [pd.to_datetime(sanitize_datetime_str(r["event_date"], r["start_time"])) for _, r in plot_df.iterrows()]
plot_df["end_datetime"] = [pd.to_datetime(sanitize_datetime_str(r["event_date"], r["end_time"])) for _, r in plot_df.iterrows()]
plot_df["TaskLabel"] = plot_df["event_name"] + " (#" + plot_df["event_id"].astype(str) + ")"

fig = px.timeline(plot_df, x_start="start_datetime", x_end="end_datetime", y="TaskLabel", color="department")
assert fig is not None
print("Timeline Plotly figure generated without errors!")

print("\n==========================================")
print("ALL TESTS PASSED WITH 100% SUCCESS!")
print("==========================================")
