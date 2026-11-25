
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import time
import html
import copy
from pathlib import Path
import matplotlib.pyplot as plt

from avl_interval_tree import Node, insert, search_overlaps
from event_manager import (
    add_event,
    get_all_events,
    check_venue_conflict
)

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EVENTFLOW | Smart Campus Management",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM DARK FRONTEND
# =========================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(37,99,235,.16), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(124,58,237,.13), transparent 25%),
        #080D19;
    color: #E5E7EB;
}
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101A2E 0%, #111827 100%);
    border-right: 1px solid #263650;
}
[data-testid="stSidebar"] * {
    color: #E2E8F0;
}
h1, h2, h3 {
    color: #F8FAFC !important;
    letter-spacing: -.4px;
}
p, label, .stMarkdown {
    color: #CBD5E1;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #14213B, #172033);
    border: 1px solid #2A4166;
    border-radius: 16px;
    padding: 17px 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,.18);
}
[data-testid="stMetricLabel"] {
    color: #A9B9D0 !important;
}
[data-testid="stMetricValue"] {
    color: #7DD3FC !important;
    font-weight: 800;
}
.stButton > button, .stFormSubmitButton > button {
    border: 1px solid #4169A5;
    border-radius: 11px;
    color: white !important;
    font-weight: 700;
    background: linear-gradient(100deg, #2563EB, #6D28D9);
    transition: all .22s ease-in-out;
    min-height: 2.65rem;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(59,130,246,.28);
    border-color: #93C5FD;
}
.stTextInput input, .stNumberInput input, .stDateInput input,
.stTimeInput input, .stTextArea textarea {
    background: #111C30 !important;
    color: #F8FAFC !important;
    border: 1px solid #344967 !important;
    border-radius: 10px !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: #111C30;
    color: #F8FAFC;
    border-color: #344967;
    border-radius: 10px;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid #2B405F;
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stExpander"] {
    background: #111C30;
    border: 1px solid #2B405F;
    border-radius: 12px;
}
hr {
    border-color: #263650;
}
[data-testid="stAlert"] {
    border-radius: 12px;
}
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #38BDF8, #8B5CF6);
}
.eyebrow {
    color: #7DD3FC;
    text-transform: uppercase;
    font-size: .76rem;
    font-weight: 800;
    letter-spacing: 2px;
}
.hero {
    background: linear-gradient(115deg, rgba(30,64,175,.42), rgba(91,33,182,.26));
    border: 1px solid rgba(125,211,252,.22);
    border-radius: 22px;
    padding: 25px 28px;
    margin-bottom: 18px;
}
.hero-title {
    color: #F8FAFC;
    font-size: 2rem;
    font-weight: 850;
    margin: 4px 0 6px 0;
}
.hero-sub {
    color: #B8C7DC;
    margin: 0;
}
.section-chip {
    display: inline-block;
    border: 1px solid #36527A;
    color: #93C5FD;
    background: #14213B;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: .75rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def to_minutes(time_value):
    hours, minutes = map(int, str(time_value).split(":")[:2])
    return hours * 60 + minutes


def minutes_to_clock(value):
    return f"{int(value) // 60:02d}:{int(value) % 60:02d}"


def get_tree_height(node):
    return 0 if node is None else node.height


def build_avl_tree(dataframe):
    tree_root = None

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
    results = []

    for _, event in dataframe.iterrows():
        event_start = to_minutes(event["start_time"])
        event_end = to_minutes(event["end_time"])

        if event_start < end and start < event_end:
            results.append(event)

    return results


def avl_search(tree_root, start, end):
    results = []
    search_overlaps(tree_root, start, end, results)
    return results


def get_tree_nodes_and_positions(tree_root):
    """Return AVL nodes positioned using an in-order layout."""

    nodes = []
    edges = []
    counter = [0]

    def walk(node, depth=0, parent_id=None):
        if node is None:
            return

        walk(node.left, depth + 1, node.event_id)

        x_index = counter[0]
        counter[0] += 1

        item = {
            "id": node.event_id,
            "name": str(node.event_name),
            "start": node.start,
            "end": node.end,
            "max_end": node.max_end,
            "height": node.height,
            "balance": get_tree_height(node.left) - get_tree_height(node.right),
            "depth": depth,
            "x_index": x_index
        }

        nodes.append(item)

        if parent_id is not None:
            edges.append((parent_id, node.event_id))

        walk(node.right, depth + 1, node.event_id)

    walk(tree_root)

    if not nodes:
        return [], [], 600, 250

    gap_x = 190
    gap_y = 145
    margin_x = 105
    margin_y = 75

    max_depth = max(item["depth"] for item in nodes)

    for item in nodes:
        item["x"] = margin_x + item["x_index"] * gap_x
        item["y"] = margin_y + item["depth"] * gap_y

    width = max(600, margin_x * 2 + (len(nodes) - 1) * gap_x)
    height = max(250, margin_y * 2 + max_depth * gap_y + 65)

    return nodes, edges, width, height


def render_animated_tree(tree_root, trace_rows=None, current_step=0):
    """Render an SVG tree with animated node and path highlighting."""

    nodes, edges, width, height = get_tree_nodes_and_positions(tree_root)

    if not nodes:
        return """
        <html><body style="background:#0B1220;color:#CBD5E1;font-family:Arial;
        display:flex;align-items:center;justify-content:center;height:100%;">
        No events available in the AVL tree.</body></html>
        """, 260

    visited_names = set()
    skipped_names = set()
    current_name = None
    current_action = None

    if trace_rows:
        for row in trace_rows[:current_step]:
            if row.get("Action") == "Visited":
                visited_names.add(str(row.get("Event")))
            elif row.get("Action", "").startswith("Skipped"):
                skipped_names.add(str(row.get("Event")))

        if 0 < current_step <= len(trace_rows):
            current_name = str(trace_rows[current_step - 1].get("Event"))
            current_action = trace_rows[current_step - 1].get("Action")

    positions = {item["id"]: item for item in nodes}

    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'xmlns="http://www.w3.org/2000/svg" role="img">'
    ]

    # Draw branches before drawing nodes.
    for parent_id, child_id in edges:
        parent = positions.get(parent_id)
        child = positions.get(child_id)

        if parent and child:
            svg_parts.append(
                f'<path class="tree-edge" d="M {parent["x"]} {parent["y"] + 37} '
                f'L {child["x"]} {child["y"] - 37}" />'
            )

    for item in nodes:
        name = item["name"]
        safe_name = html.escape(name[:19])

        interval = (
            f'{minutes_to_clock(item["start"])}–'
            f'{minutes_to_clock(item["end"])}'
        )

        is_current = name == current_name

        if is_current and current_action == "Visited":
            css_class = "node-current"
        elif is_current and current_action and current_action.startswith("Skipped"):
            css_class = "node-skipped"
        elif name in visited_names:
            css_class = "node-visited"
        else:
            css_class = "node-default"

        x, y = item["x"], item["y"]

        svg_parts.append(f"""
        <g class="tree-node {css_class}" transform="translate({x},{y})">
          <rect x="-76" y="-37" width="152" height="74" rx="15" />
          <text class="node-name" x="0" y="-13">{safe_name}</text>
          <text class="node-interval" x="0" y="5">{interval}</text>
          <text class="node-meta" x="0" y="23">
            H:{item['height']}  BF:{item['balance']}  Max:{minutes_to_clock(item['max_end'])}
          </text>
        </g>
        """)

    svg_parts.append("</svg>")

    document = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * {{ box-sizing: border-box; }}

      body {{
        margin: 0;
        padding: 12px;
        background: radial-gradient(circle at 50% 0%, #172B4D, #0B1220 65%);
        font-family: Inter, Segoe UI, Arial, sans-serif;
        overflow-x: auto;
      }}

      .canvas {{
        min-width: {min(width, 10000)}px;
        animation: canvasIn .5s ease-out both;
      }}

      svg {{
        overflow: visible;
      }}

      .tree-edge {{
        fill: none;
        stroke: #456184;
        stroke-width: 4;
        stroke-linecap: round;
        opacity: .9;
        stroke-dasharray: 10 7;
        animation: drawEdge .65s ease-out both;
      }}

      .tree-node rect {{
        stroke-width: 2.5;
        filter: drop-shadow(0 7px 9px rgba(0,0,0,.35));
        transition: fill .3s ease, stroke .3s ease, filter .3s ease;
      }}

      .node-default rect {{
        fill: #172943;
        stroke: #456184;
      }}

      .node-visited rect {{
        fill: #123D54;
        stroke: #22D3EE;
      }}

      .node-current rect {{
        fill: #164E63;
        stroke: #67E8F9;
        stroke-width: 4;
        filter: drop-shadow(0 0 13px rgba(34,211,238,.7));
        animation: pulseNode 1.25s ease-in-out infinite;
      }}

      .node-skipped rect {{
        fill: #4A2634;
        stroke: #FB7185;
      }}

      .node-name {{
        fill: #F8FAFC;
        font-size: 14px;
        font-weight: 800;
        text-anchor: middle;
      }}

      .node-interval {{
        fill: #BAE6FD;
        font-size: 12px;
        font-weight: 700;
        text-anchor: middle;
      }}

      .node-meta {{
        fill: #A9BDD4;
        font-size: 9px;
        text-anchor: middle;
      }}

      .tree-node {{
        transform-box: fill-box;
        transform-origin: center;
        animation: nodeEnter .45s cubic-bezier(.2,.8,.2,1) both;
      }}

      @keyframes nodeEnter {{
        from {{ opacity: 0; scale: .55; }}
        to {{ opacity: 1; scale: 1; }}
      }}

      @keyframes drawEdge {{
        from {{ stroke-dashoffset: 35; opacity: .1; }}
        to {{ stroke-dashoffset: 0; opacity: .9; }}
      }}

      @keyframes pulseNode {{
        0%,100% {{ filter: drop-shadow(0 0 5px rgba(34,211,238,.35)); }}
        50% {{ filter: drop-shadow(0 0 18px rgba(34,211,238,.9)); }}
      }}

      @keyframes canvasIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
    </head>
    <body>
      <div class="canvas">{''.join(svg_parts)}</div>
    </body>
    </html>
    """

    return document, min(max(height + 30, 280), 900)


def make_insertion_snapshots(dataframe):
    """Capture the balanced tree after each inserted event."""

    snapshots = []
    working_root = None

    ordered = dataframe.sort_values(
        by=["start_time", "event_id"]
    ).reset_index(drop=True)

    for _, event in ordered.iterrows():
        working_root = insert(
            working_root,
            Node(
                int(event["event_id"]),
                str(event["event_name"]),
                to_minutes(event["start_time"]),
                to_minutes(event["end_time"])
            )
        )

        snapshots.append(copy.deepcopy(working_root))

    return snapshots, ordered


# =========================================================
# LOAD CSV + LIVE SQLITE EVENTS
# =========================================================

file_path = Path(__file__).with_name("events.csv")

csv_events = pd.read_csv(file_path)

csv_events["department"] = "Existing Dataset"
csv_events["event_date"] = "Sample Schedule"
csv_events["source"] = "CSV"

database_records = get_all_events()

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

if not db_events.empty:
    next_id = int(csv_events["event_id"].max()) + 1
    db_events["event_id"] = range(next_id, next_id + len(db_events))
    db_events["source"] = "Live Booking"

else:
    db_events = pd.DataFrame(
        columns=[
            "db_event_id",
            "event_name",
            "department",
            "venue",
            "event_date",
            "start_time",
            "end_time",
            "event_id",
            "source"
        ]
    )

events = pd.concat(
    [csv_events, db_events],
    ignore_index=True
)

events["event_id"] = events["event_id"].astype(int)

root = build_avl_tree(events)

# =========================================================
# HERO + OVERVIEW
# =========================================================

st.markdown("""
<div class="hero">
  <div class="eyebrow">SMART CAMPUS SCHEDULING PLATFORM</div>
  <div class="hero-title">EVENTFLOW</div>
  <p class="hero-sub">
    Intelligent event scheduling powered by AVL Interval Trees,
    live venue booking and conflict detection.
  </p>
</div>
""", unsafe_allow_html=True)

live_count = len(db_events)
sample_count = len(csv_events)
venue_count = events["venue"].nunique() if not events.empty else 0

metric_cols = st.columns(4)

metric_cols[0].metric("Total Events", len(events))
metric_cols[1].metric("Live Bookings", live_count)
metric_cols[2].metric("Venues", venue_count)
metric_cols[3].metric("Search Engine", "AVL + Linear")

st.markdown(
    '<span class="section-chip">CAMPUS EVENT DATA</span>',
    unsafe_allow_html=True
)

st.subheader("📋 Campus Event Records")

display_columns = [
    "event_id",
    "event_name",
    "department",
    "venue",
    "event_date",
    "start_time",
    "end_time",
    "source"
]

st.dataframe(
    events[display_columns],
    use_container_width=True,
    hide_index=True
)

count_cols = st.columns(2)

count_cols[0].metric("Live Campus Bookings", live_count)
count_cols[1].metric("Existing Sample Events", sample_count)

# =========================================================
# INTERVAL SEARCH
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">ALGORITHM LAB</span>',
    unsafe_allow_html=True
)

st.header("🔍 Interval Search")

search_method = st.radio(
    "Choose search algorithm",
    ["Linear Search", "AVL Interval Tree"],
    horizontal=True
)

search_col1, search_col2 = st.columns(2)

with search_col1:
    start_time = st.time_input(
        "Query start time",
        value=pd.to_datetime("10:00").time(),
        key="main_search_start"
    )

with search_col2:
    end_time = st.time_input(
        "Query end time",
        value=pd.to_datetime("11:00").time(),
        key="main_search_end"
    )

if st.button("🚀 Search Overlapping Events", key="main_search_button"):

    start = start_time.hour * 60 + start_time.minute
    end = end_time.hour * 60 + end_time.minute

    if start >= end:
        st.error("End time must be after start time.")

    else:
        begin = time.perf_counter()

        if search_method == "Linear Search":
            results = linear_search(events, start, end)
        else:
            results = avl_search(root, start, end)

        elapsed = time.perf_counter() - begin

        if results:

            if search_method == "Linear Search":
                result_rows = [
                    {
                        "Event": row["event_name"],
                        "Start": row["start_time"],
                        "End": row["end_time"],
                        "Venue": row["venue"],
                        "Date": row["event_date"]
                    }
                    for row in results
                ]

            else:
                result_rows = [
                    {
                        "Event": node.event_name,
                        "Start": minutes_to_clock(node.start),
                        "End": minutes_to_clock(node.end)
                    }
                    for node in results
                ]

            st.dataframe(
                pd.DataFrame(result_rows),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No overlapping events found for this interval.")

        result_cols = st.columns(2)

        result_cols[0].metric("Overlapping Events", len(results))
        result_cols[1].metric("Execution Time", f"{elapsed:.8f} sec")

# =========================================================
# SMART VENUE CONFLICT DETECTOR
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">VENUE INTELLIGENCE</span>',
    unsafe_allow_html=True
)

st.header("🚨 Smart Campus Venue Conflict Detector")

st.write(
    "Detect overlapping bookings at the same venue on the same date."
)

conflicts = []

for i in range(len(events)):

    for j in range(i + 1, len(events)):

        event1 = events.iloc[i]
        event2 = events.iloc[j]

        same_venue = (
            str(event1["venue"]).strip().lower()
            == str(event2["venue"]).strip().lower()
        )

        same_date = (
            str(event1["event_date"])
            == str(event2["event_date"])
        )

        if not same_venue or not same_date:
            continue

        start1 = to_minutes(event1["start_time"])
        end1 = to_minutes(event1["end_time"])

        start2 = to_minutes(event2["start_time"])
        end2 = to_minutes(event2["end_time"])

        if start1 < end2 and start2 < end1:

            overlap_start = max(start1, start2)
            overlap_end = min(end1, end2)

            conflicts.append({
                "Venue": event1["venue"],
                "Date": event1["event_date"],
                "Event 1": event1["event_name"],
                "Event 2": event2["event_name"],
                "Conflict Starts": minutes_to_clock(overlap_start),
                "Conflict Ends": minutes_to_clock(overlap_end),
                "Overlap Duration (minutes)": overlap_end - overlap_start
            })

conflict_col1, conflict_col2 = st.columns(2)

conflict_col1.metric("Total Venue Conflicts", len(conflicts))

conflict_col2.metric(
    "Conflict Status",
    "Action Required" if conflicts else "Clear"
)

if conflicts:

    st.error("Venue scheduling conflicts detected.")

    st.dataframe(
        pd.DataFrame(conflicts),
        use_container_width=True,
        hide_index=True
    )

else:
    st.success("No venue conflicts detected.")

# =========================================================
# SMART SLOT RECOMMENDATION
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">SMART SCHEDULER</span>',
    unsafe_allow_html=True
)

st.header("🕒 Smart Venue Slot Recommendation")

st.write("Find available time windows for a venue and date.")

slot_col1, slot_col2 = st.columns(2)

with slot_col1:
    selected_venue = st.selectbox(
        "Select venue",
        [
            "Auditorium",
            "Seminar Hall",
            "Lab 1",
            "Lab 2",
            "Lab 3",
            "Conference Room",
            "Classroom 1"
        ],
        key="slot_venue"
    )

with slot_col2:
    selected_date = st.date_input(
        "Select event date",
        key="slot_date"
    )

required_duration = st.select_slider(
    "Minimum event duration",
    options=[30, 60, 90, 120, 150, 180],
    value=60,
    format_func=lambda value: f"{value} min",
    key="slot_duration_v2"
)

if st.button("✨ Find Available Slots", key="find_slots"):

    selected_date_text = selected_date.strftime("%Y-%m-%d")

    selected_events = events[
        (
            events["venue"].astype(str).str.strip().str.lower()
            == selected_venue.lower()
        )
        &
        (
            events["event_date"].astype(str)
            == selected_date_text
        )
    ].copy()

    working_start = 9 * 60
    working_end = 17 * 60

    occupied = []

    for _, event in selected_events.iterrows():

        start = max(
            to_minutes(event["start_time"]),
            working_start
        )

        end = min(
            to_minutes(event["end_time"]),
            working_end
        )

        if start < end:
            occupied.append((start, end))

    occupied.sort()

    merged = []

    for start, end in occupied:

        if not merged or start > merged[-1][1]:
            merged.append([start, end])

        else:
            merged[-1][1] = max(
                merged[-1][1],
                end
            )

    available = []
    current = working_start

    for start, end in merged:

        if start - current >= required_duration:

            available.append({
                "Available Start": minutes_to_clock(current),
                "Available End": minutes_to_clock(start),
                "Available Duration": f"{start - current} minutes"
            })

        current = max(current, end)

    if working_end - current >= required_duration:

        available.append({
            "Available Start": minutes_to_clock(current),
            "Available End": minutes_to_clock(working_end),
            "Available Duration": f"{working_end - current} minutes"
        })

    st.subheader(
        f"Availability for {selected_venue} · {selected_date_text}"
    )

    if available:

        st.success(
            f"{len(available)} suitable free window(s) found."
        )

        st.dataframe(
            pd.DataFrame(available),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.warning("No suitable time window found for the selected duration.")

    if not selected_events.empty:

        st.caption("Existing bookings for this venue and date")

        st.dataframe(
            selected_events[
                ["event_name", "start_time", "end_time"]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No existing bookings. The venue is free from 09:00 to 17:00."
        )

# =========================================================
# VISUAL EVENT TIMELINE
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">SCHEDULE VISUALIZATION</span>',
    unsafe_allow_html=True
)

st.header("📊 Visual Event Timeline")

if not events.empty:

    timeline_data = events.copy().reset_index(drop=True)

    fig, ax = plt.subplots(
        figsize=(13, max(4, len(timeline_data) * .38))
    )

    fig.patch.set_facecolor("#0B1220")
    ax.set_facecolor("#111C30")

    for index, event in timeline_data.iterrows():

        start = to_minutes(event["start_time"])
        end = to_minutes(event["end_time"])

        ax.barh(
            event["event_name"],
            end - start,
            left=start,
            height=.58,
            color=(
                "#38BDF8"
                if event["source"] == "CSV"
                else "#A78BFA"
            ),
            edgecolor="#E0F2FE",
            linewidth=.7
        )

        ax.text(
            start + 2,
            index,
            f"{event['start_time']}–{event['end_time']}",
            va="center",
            color="#F8FAFC",
            fontsize=8
        )

    ax.set_xlim(8 * 60, 18 * 60)

    ax.set_xticks(range(9 * 60, 18 * 60, 60))

    ax.set_xticklabels(
        [f"{hour:02d}:00" for hour in range(9, 18)],
        color="#CBD5E1"
    )

    ax.tick_params(
        axis="y",
        colors="#E2E8F0",
        labelsize=8
    )

    ax.set_xlabel("Time of day", color="#CBD5E1")
    ax.set_ylabel("Campus events", color="#CBD5E1")

    ax.grid(
        axis="x",
        linestyle="--",
        alpha=.2,
        color="#94A3B8"
    )

    for spine in ax.spines.values():
        spine.set_color("#334155")

    plt.tight_layout()

    st.pyplot(fig, use_container_width=True)

    plt.close(fig)

else:
    st.info("No events available for the timeline.")

# =========================================================
# PERFORMANCE ANALYZER
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">ALGORITHM PERFORMANCE</span>',
    unsafe_allow_html=True
)

st.header("⚡ Advanced Performance Analyzer")

st.write(
    "Compare the execution time of Linear Search and AVL Interval Tree."
)

repetitions = st.selectbox(
    "Number of repetitions",
    [100, 500, 1000, 5000],
    index=1
)

if st.button("📈 Run Performance Analysis"):

    query_start = 10 * 60
    query_end = 11 * 60

    linear_begin = time.perf_counter()

    for _ in range(repetitions):
        linear_results = linear_search(
            events,
            query_start,
            query_end
        )

    linear_duration = time.perf_counter() - linear_begin

    avl_begin = time.perf_counter()

    for _ in range(repetitions):
        avl_results = avl_search(
            root,
            query_start,
            query_end
        )

    avl_duration = time.perf_counter() - avl_begin

    comparison = pd.DataFrame({
        "Algorithm": [
            "Linear Search",
            "AVL Interval Tree"
        ],
        "Execution Time (seconds)": [
            linear_duration,
            avl_duration
        ],
        "Matching Events": [
            len(linear_results),
            len(avl_results)
        ]
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        comparison.set_index("Algorithm")[
            "Execution Time (seconds)"
        ]
    )

    if len(linear_results) == len(avl_results):

        st.success(
            "Both algorithms returned the same number of matching events."
        )

    else:

        st.error(
            "The result counts differ. Check the AVL interval-tree implementation."
        )

# =========================================================
# DYNAMIC EVENT MANAGEMENT
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">DATASET MANAGEMENT</span>',
    unsafe_allow_html=True
)

st.header("➕ Add a New Sample Event")

st.caption(
    "This form appends a demonstration event to events.csv. "
    "Use Live Campus Event Booking for dated database bookings."
)

with st.form("add_event_form"):

    new_event_name = st.text_input("Event name")

    new_start = st.time_input(
        "Event start time",
        value=pd.to_datetime("09:00").time(),
        key="new_start"
    )

    new_end = st.time_input(
        "Event end time",
        value=pd.to_datetime("10:00").time(),
        key="new_end"
    )

    new_venue = st.text_input("Event venue")

    submit_event = st.form_submit_button("Add Sample Event")

    if submit_event:

        start = new_start.hour * 60 + new_start.minute
        end = new_end.hour * 60 + new_end.minute

        if not new_event_name.strip():

            st.error("Please enter an event name.")

        elif not new_venue.strip():

            st.error("Please enter an event venue.")

        elif start >= end:

            st.error("End time must be after start time.")

        else:

            new_event = pd.DataFrame([{
                "event_id": int(events["event_id"].max()) + 1,
                "event_name": new_event_name.strip(),
                "start_time": new_start.strftime("%H:%M"),
                "end_time": new_end.strftime("%H:%M"),
                "venue": new_venue.strip()
            }])

            new_event.to_csv(
                file_path,
                mode="a",
                header=False,
                index=False
            )

            st.success("Sample event added successfully.")

            st.rerun()

# =========================================================
# REALISTIC AVL TREE VISUALIZER
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">INTERACTIVE DATA STRUCTURE LAB</span>',
    unsafe_allow_html=True
)

st.header("🌳 Realistic AVL Interval Tree Visualizer")

st.write(
    "Explore the balanced tree structure. Nodes show event intervals, "
    "height, balance factor and maximum end time."
)

tree_tab, insert_tab = st.tabs([
    "🔎 Live Search Tree",
    "🌱 Insertion Replay"
])

with tree_tab:

    st.markdown("**Node colour guide:**")

    legend1, legend2, legend3, legend4 = st.columns(4)

    legend1.markdown("🔵 **Unvisited**")
    legend2.markdown("🟢 **Visited**")
    legend3.markdown("🟡 **Current node**")
    legend4.markdown("🔴 **Skipped**")

    if root is not None:

        tree_html, tree_height = render_animated_tree(root)

        st.components.v1.html(
            tree_html,
            height=tree_height,
            scrolling=True
        )

        tree_nodes, _, _, _ = get_tree_nodes_and_positions(root)

        tree_metrics = st.columns(3)

        tree_metrics[0].metric("Tree Nodes", len(tree_nodes))
        tree_metrics[1].metric("Tree Height", get_tree_height(root))
        tree_metrics[2].metric("Root Event", root.event_name)

        st.subheader("🔬 Inspect a Tree Node")

        event_options = {
            f"{row['event_name']} (ID: {row['event_id']})":
            int(row["event_id"])
            for _, row in events.iterrows()
        }

        selected_event_label = st.selectbox(
            "Select an event",
            list(event_options.keys()),
            key="avl_inspector"
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

        selected_node = find_node(root, selected_id)

        if selected_node:

            balance = (
                get_tree_height(selected_node.left)
                - get_tree_height(selected_node.right)
            )

            info_cols = st.columns(3)

            info_cols[0].metric("Height", selected_node.height)

            info_cols[1].metric(
                "Balance Factor",
                balance
            )

            info_cols[2].metric(
                "Maximum End",
                minutes_to_clock(selected_node.max_end)
            )

            st.write(f"**Event:** {selected_node.event_name}")

            st.write(
                f"**Interval:** "
                f"{minutes_to_clock(selected_node.start)} – "
                f"{minutes_to_clock(selected_node.end)}"
            )

            st.write(
                "**Left child:**",
                selected_node.left.event_name
                if selected_node.left else "None"
            )

            st.write(
                "**Right child:**",
                selected_node.right.event_name
                if selected_node.right else "None"
            )

    else:

        st.info("No events available to visualize.")

with insert_tab:

    st.write(
        "Replay the tree after each event insertion. "
        "The AVL insert function automatically balances the tree at every step."
    )

    if not events.empty:

        snapshots, insertion_order = make_insertion_snapshots(events)

        if "insertion_step" not in st.session_state:
            st.session_state.insertion_step = len(snapshots)

        st.session_state.insertion_step = min(
            max(1, st.session_state.insertion_step),
            len(snapshots)
        )

        if "insert_step_slider" not in st.session_state:
            st.session_state.insert_step_slider = (
                st.session_state.insertion_step
            )

        insert_controls = st.columns(3)

        if insert_controls[0].button(
            "◀ Previous insertion",
            key="insert_prev"
        ):

            st.session_state.insertion_step = max(
                1,
                st.session_state.insertion_step - 1
            )

            st.session_state.insert_step_slider = (
                st.session_state.insertion_step
            )

        if insert_controls[1].button(
            "Next insertion ▶",
            key="insert_next"
        ):

            st.session_state.insertion_step = min(
                len(snapshots),
                st.session_state.insertion_step + 1
            )

            st.session_state.insert_step_slider = (
                st.session_state.insertion_step
            )

        if insert_controls[2].button(
            "↺ Start over",
            key="insert_reset"
        ):

            st.session_state.insertion_step = 1
            st.session_state.insert_step_slider = 1

        chosen_step = st.slider(
            "Insertion step",
            min_value=1,
            max_value=len(snapshots),
            key="insert_step_slider"
        )

        st.session_state.insertion_step = chosen_step

        inserted_event = insertion_order.iloc[chosen_step - 1]

        st.progress(chosen_step / len(snapshots))

        st.info(
            f"Step {chosen_step} of {len(snapshots)} · "
            f"Inserted: {inserted_event['event_name']} · "
            f"Interval: {inserted_event['start_time']}–"
            f"{inserted_event['end_time']}"
        )

        snapshot_html, snapshot_height = render_animated_tree(
            snapshots[chosen_step - 1]
        )

        st.components.v1.html(
            snapshot_html,
            height=snapshot_height,
            scrolling=True
        )

    else:

        st.info("No events are available for insertion replay.")

# =========================================================
# AUTOMATIC AVL SEARCH ANIMATION
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">STEP-BY-STEP ALGORITHM ANIMATION</span>',
    unsafe_allow_html=True
)

st.header("🎬 Animated AVL Interval Search")

st.write(
    "Watch the actual tree highlight each node as the AVL interval search traverses it."
)

trace_col1, trace_col2 = st.columns(2)

with trace_col1:

    trace_start = st.time_input(
        "Search start time",
        value=pd.to_datetime("10:00").time(),
        key="trace_start"
    )

with trace_col2:

    trace_end = st.time_input(
        "Search end time",
        value=pd.to_datetime("11:00").time(),
        key="trace_end"
    )

if "avl_trace_data" not in st.session_state:
    st.session_state.avl_trace_data = []

if "avl_match_data" not in st.session_state:
    st.session_state.avl_match_data = []

if "avl_current_step" not in st.session_state:
    st.session_state.avl_current_step = 1

if "avl_playing" not in st.session_state:
    st.session_state.avl_playing = False

if "avl_last_refresh" not in st.session_state:
    st.session_state.avl_last_refresh = -1

if "trace_step_slider" not in st.session_state:
    st.session_state.trace_step_slider = (
        st.session_state.avl_current_step
    )

if st.button(
    "▶ Generate New Search Animation",
    key="auto_new_search"
):

    start_minutes = trace_start.hour * 60 + trace_start.minute
    end_minutes = trace_end.hour * 60 + trace_end.minute

    if start_minutes >= end_minutes:

        st.error("End time must be later than start time.")

    else:

        new_trace = []
        new_matches = []

        search_overlaps(
            root,
            start_minutes,
            end_minutes,
            new_matches,
            new_trace
        )

        st.session_state.avl_trace_data = new_trace

        st.session_state.avl_match_data = [
            {
                "Event": node.event_name,
                "Start": minutes_to_clock(node.start),
                "End": minutes_to_clock(node.end)
            }
            for node in new_matches
        ]

        st.session_state.avl_current_step = 1
        st.session_state.trace_step_slider = 1
        st.session_state.avl_playing = False
        st.session_state.avl_last_refresh = -1

trace_data = st.session_state.avl_trace_data
match_data = st.session_state.avl_match_data

if trace_data:

    total_steps = len(trace_data)

    speed_label = st.select_slider(
        "Animation speed",
        options=["Slow", "Normal", "Fast"],
        value="Normal",
        key="animation_speed_v2"
    )

    refresh_interval = {
        "Slow": 1800,
        "Normal": 1000,
        "Fast": 450
    }[speed_label]

    control_cols = st.columns(4)

    if control_cols[0].button(
        "⏮ Previous",
        key="trace_previous"
    ):

        st.session_state.avl_playing = False

        st.session_state.avl_current_step = max(
            1,
            st.session_state.avl_current_step - 1
        )

        st.session_state.trace_step_slider = (
            st.session_state.avl_current_step
        )

    if control_cols[1].button(
        "⏸ Pause" if st.session_state.avl_playing else "▶ Play",
        key="trace_play_pause"
    ):

        st.session_state.avl_playing = not st.session_state.avl_playing

    if control_cols[2].button(
        "Next ⏭",
        key="trace_next"
    ):

        st.session_state.avl_playing = False

        st.session_state.avl_current_step = min(
            total_steps,
            st.session_state.avl_current_step + 1
        )

        st.session_state.trace_step_slider = (
            st.session_state.avl_current_step
        )

    if control_cols[3].button(
        "↻ Reset",
        key="trace_reset"
    ):

        st.session_state.avl_playing = False
        st.session_state.avl_current_step = 1
        st.session_state.trace_step_slider = 1

    if (
        st.session_state.avl_playing
        and st.session_state.avl_current_step < total_steps
    ):

        refresh_count = st_autorefresh(
            interval=refresh_interval,
            key="avl_visual_auto_refresh"
        )

        if refresh_count != st.session_state.avl_last_refresh:

            st.session_state.avl_last_refresh = refresh_count

            st.session_state.avl_current_step = min(
                total_steps,
                st.session_state.avl_current_step + 1
            )

            st.session_state.trace_step_slider = (
                st.session_state.avl_current_step
            )

    elif st.session_state.avl_current_step >= total_steps:

        st.session_state.avl_playing = False

    st.session_state.avl_current_step = min(
        max(1, st.session_state.avl_current_step),
        total_steps
    )

    slider_step = st.slider(
        "Traversal step",
        min_value=1,
        max_value=total_steps,
        key="trace_step_slider"
    )

    st.session_state.avl_current_step = slider_step

    current_step = st.session_state.avl_current_step
    current_row = trace_data[current_step - 1]

    st.progress(current_step / total_steps)

    status_cols = st.columns(3)

    status_cols[0].metric(
        "Current Step",
        f"{current_step}/{total_steps}"
    )

    status_cols[1].metric(
        "Nodes Visited",
        sum(
            1 for row in trace_data[:current_step]
            if row.get("Action") == "Visited"
        )
    )

    status_cols[2].metric(
        "Matching Events",
        len(match_data)
    )

    animated_html, animated_height = render_animated_tree(
        root,
        trace_rows=trace_data,
        current_step=current_step
    )

    st.components.v1.html(
        animated_html,
        height=animated_height,
        scrolling=True
    )

    if current_row.get("Action") == "Visited":

        st.success(
            f"🔎 Visiting node: {current_row.get('Event')}"
        )

    else:

        st.warning(
            f"⏭ {current_row.get('Action')}: "
            f"{current_row.get('Event')}"
        )

    detail_cols = st.columns(3)

    detail_cols[0].metric(
        "Interval Start",
        minutes_to_clock(current_row["Start"])
    )

    detail_cols[1].metric(
        "Interval End",
        minutes_to_clock(current_row["End"])
    )

    detail_cols[2].metric(
        "Subtree Max End",
        minutes_to_clock(current_row["Max End"])
    )

    with st.expander("📜 Traversal history", expanded=True):

        history_df = pd.DataFrame(
            trace_data[:current_step]
        )

        for column in ["Start", "End", "Max End"]:

            if column in history_df.columns:
                history_df[column] = history_df[column].apply(
                    minutes_to_clock
                )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("🎯 Matching Events")

    if match_data:

        st.dataframe(
            pd.DataFrame(match_data),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No overlapping events were found for this query.")

    if current_step == total_steps:

        st.success("AVL search animation completed.")

else:

    st.info(
        "Choose a time interval and click Generate New Search Animation to begin."
    )

# =========================================================
# LIVE CAMPUS EVENT BOOKING
# =========================================================

st.divider()

st.markdown(
    '<span class="section-chip">LIVE DATABASE BOOKING</span>',
    unsafe_allow_html=True
)

st.header("🏫 Live Campus Event Booking")

st.write(
    "Register a campus event. The system checks for a venue conflict before saving it."
)

with st.form("live_campus_booking"):

    booking_name = st.text_input(
        "Event name",
        placeholder="Example: AI Symposium"
    )

    department = st.selectbox(
        "Department",
        [
            "Computer Science",
            "Data Science",
            "Artificial Intelligence",
            "Electronics",
            "Mechanical",
            "Civil",
            "Other"
        ]
    )

    booking_venue = st.selectbox(
        "Select venue",
        [
            "Auditorium",
            "Seminar Hall",
            "Lab 1",
            "Lab 2",
            "Lab 3",
            "Conference Room",
            "Classroom 1"
        ]
    )

    booking_date = st.date_input("Event date")

    booking_col1, booking_col2 = st.columns(2)

    with booking_col1:

        booking_start = st.time_input(
            "Start time",
            value=pd.to_datetime("10:00").time(),
            key="booking_start"
        )

    with booking_col2:

        booking_end = st.time_input(
            "End time",
            value=pd.to_datetime("11:00").time(),
            key="booking_end"
        )

    submit_booking = st.form_submit_button(
        "🚀 Check & Book Venue"
    )

    if submit_booking:

        start_text = booking_start.strftime("%H:%M")
        end_text = booking_end.strftime("%H:%M")
        date_text = booking_date.strftime("%Y-%m-%d")

        if not booking_name.strip():

            st.error("Please enter an event name.")

        elif booking_start >= booking_end:

            st.error("End time must be later than start time.")

        else:

            booking_conflicts = check_venue_conflict(
                booking_venue,
                date_text,
                start_text,
                end_text
            )

            if booking_conflicts:

                st.error(
                    "Venue booking conflict detected. Choose another time."
                )

                st.dataframe(
                    pd.DataFrame(
                        booking_conflicts,
                        columns=[
                            "Event ID",
                            "Existing Event",
                            "Start Time",
                            "End Time"
                        ]
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                add_event(
                    booking_name.strip(),
                    department,
                    booking_venue,
                    date_text,
                    start_text,
                    end_text
                )

                st.success(
                    f"{booking_name} booked successfully!"
                )

                st.rerun()

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    "<div style='text-align:center;color:#64748B;padding:12px;'>"
    "EVENTFLOW · Smart Event and Interval Query Management · "
    "Powered by AVL Interval Trees and SQLite"
    "</div>",
    unsafe_allow_html=True
)
