"""
EVENTFLOW - Central Data Loader & Core Helper Utilities
Unifies CSV dataset and SQLite database bookings, builds the AVL Interval Tree,
and provides time conversion and tree utilities.
"""

from pathlib import Path
import pandas as pd
import html
from avl_interval_tree import Node, insert, search_overlaps
from event_manager import get_all_events, check_venue_conflict

CSV_PATH = Path(__file__).resolve().parent.parent / "events.csv"

# Pre-mapped departments for sample CSV events for realistic campus analytics
CSV_DEPARTMENT_MAP = {
    "Symposium": "Computer Science",
    "Workshop": "Electronics",
    "Seminar": "Mechanical",
    "Project Expo": "Information Tech",
    "Coding Contest": "Computer Science",
    "Guest Lecture": "Data Science",
    "AI Workshop": "Artificial Intelligence",
    "Tech Talk": "Cyber Security",
    "Paper Presentation": "Civil Engineering",
    "Robotics Demo": "Electronics"
}

def to_minutes(time_value):
    """Convert HH:MM string to integer minutes from midnight."""
    if pd.isna(time_value):
        return 0
    parts = str(time_value).strip().split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
    return hours * 60 + minutes

def minutes_to_clock(value):
    """Convert integer minutes from midnight to HH:MM format."""
    val = int(value)
    hours = (val // 60) % 24
    minutes = val % 60
    return f"{hours:02d}:{minutes:02d}"

def get_tree_height(node):
    """Return height of node or 0 if None."""
    return 0 if node is None else node.height

def build_avl_tree(dataframe):
    """Constructs an AVL Interval Tree from a pandas DataFrame of events."""
    tree_root = None
    if dataframe.empty:
        return None

    for _, event in dataframe.iterrows():
        tree_root = insert(
            tree_root,
            Node(
                int(event["event_id"]),
                str(event["event_name"]),
                to_minutes(event["start_time"]),
                to_minutes(event["end_time"])
            )
        )
    return tree_root

def linear_search(dataframe, start, end):
    """Baseline O(n) linear search over DataFrame for overlapping intervals."""
    results = []
    for _, event in dataframe.iterrows():
        event_start = to_minutes(event["start_time"])
        event_end = to_minutes(event["end_time"])
        if event_start < end and start < event_end:
            results.append(event)
    return results

def avl_search(tree_root, start, end):
    """AVL tree interval search returning matching nodes."""
    results = []
    search_overlaps(tree_root, start, end, results)
    return results

def load_unified_events():
    """
    Loads both CSV events and Live SQLite database events into a single unified DataFrame.
    Guarantees unique event_id across all records and builds the primary AVL tree.
    """
    # 1. Read CSV baseline events
    if CSV_PATH.exists():
        csv_events = pd.read_csv(CSV_PATH)
    else:
        csv_events = pd.DataFrame(columns=["event_id", "event_name", "start_time", "end_time", "venue"])

    csv_events["event_id"] = csv_events["event_id"].astype(int)
    csv_events["department"] = csv_events["event_name"].map(
        lambda name: CSV_DEPARTMENT_MAP.get(name, "Academic Affairs")
    )
    csv_events["event_date"] = "2026-11-25"
    csv_events["source"] = "CSV Seed"

    # 2. Read SQLite live bookings
    database_records = get_all_events()
    if database_records:
        db_events = pd.DataFrame(
            database_records,
            columns=[
                "db_event_id",
                "event_name",
                "department",
                "venue",
                "event_date",
                "start_time",
                "end_time"
            ]
        )
        max_csv_id = int(csv_events["event_id"].max()) if not csv_events.empty else 0
        db_events["event_id"] = range(max_csv_id + 1, max_csv_id + 1 + len(db_events))
        db_events["source"] = "Live SQLite"
    else:
        db_events = pd.DataFrame(columns=[
            "db_event_id", "event_name", "department", "venue",
            "event_date", "start_time", "end_time", "event_id", "source"
        ])

    # 3. Concatenate and clean
    unified = pd.concat([csv_events, db_events], ignore_index=True)
    unified["event_id"] = unified["event_id"].astype(int)
    unified["start_minutes"] = unified["start_time"].apply(to_minutes)
    unified["end_minutes"] = unified["end_time"].apply(to_minutes)
    unified["duration_minutes"] = unified["end_minutes"] - unified["start_minutes"]

    # 4. Build AVL Interval Tree
    root = build_avl_tree(unified)

    return unified, csv_events, db_events, root

def count_all_venue_conflicts(events_df):
    """Calculates all pairwise venue conflicts on the unified dataset."""
    conflicts = []
    n = len(events_df)
    for i in range(n):
        for j in range(i + 1, n):
            e1 = events_df.iloc[i]
            e2 = events_df.iloc[j]

            same_venue = str(e1["venue"]).strip().lower() == str(e2["venue"]).strip().lower()
            same_date = str(e1["event_date"]).strip() == str(e2["event_date"]).strip()

            if not (same_venue and same_date):
                continue

            s1, e1_end = e1["start_minutes"], e1["end_minutes"]
            s2, e2_end = e2["start_minutes"], e2["end_minutes"]

            if s1 < e2_end and s2 < e1_end:
                overlap_s = max(s1, s2)
                overlap_e = min(e1_end, e2_end)
                conflicts.append({
                    "venue": e1["venue"],
                    "date": e1["event_date"],
                    "event_1_id": e1["event_id"],
                    "event_1_name": e1["event_name"],
                    "event_2_id": e2["event_id"],
                    "event_2_name": e2["event_name"],
                    "conflict_start": minutes_to_clock(overlap_s),
                    "conflict_end": minutes_to_clock(overlap_e),
                    "duration": overlap_e - overlap_s
                })
    return conflicts
