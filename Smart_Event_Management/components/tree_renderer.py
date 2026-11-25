"""
EVENTFLOW - Master AVL Tree Rendering Engine
Provides large, ultra-crisp, perfectly centered SVG tree layouts with
guaranteed zero cut-offs, smart responsive auto-fitting, native scrollbars,
drag-to-pan, interactive zoom controls, and 5-line detailed node cards.
"""

import html
import copy
from avl_interval_tree import Node, insert, update, get_balance, right_rotate, left_rotate
from components.data_loader import to_minutes, minutes_to_clock, get_tree_height

CARD_W = 186
CARD_H = 96
H_GAP = 32
V_GAP = 76
MARGIN_TOP = 80
MARGIN_SIDE = 70


def get_tree_nodes_and_positions(tree_root):
    """
    Computes hierarchical bottom-up positions so parent nodes are centered above their subtrees.
    Guarantees that leaves and branches never overlap and the entire tree is centered horizontally.
    """
    if not tree_root:
        return [], [], 860, 360

    def compute(node, depth=0):
        if not node:
            return [], [], 0, 0

        l_nodes, l_edges, l_w, l_rx = compute(node.left, depth + 1)
        r_nodes, r_edges, r_w, r_rx = compute(node.right, depth + 1)

        if l_w > 0 and r_w > 0:
            r_shift = l_w + H_GAP
            for rn in r_nodes:
                rn['x'] += r_shift
            root_x = (l_rx + r_rx + r_shift) / 2
            total_w = l_w + H_GAP + r_w
        elif l_w > 0:
            root_x = l_w
            total_w = l_w + CARD_W / 2
        elif r_w > 0:
            root_x = CARD_W / 2
            r_shift = CARD_W / 2 + H_GAP
            for rn in r_nodes:
                rn['x'] += r_shift
            total_w = r_shift + r_w
        else:
            root_x = CARD_W / 2
            total_w = CARD_W

        cur_node = {
            'id': int(node.event_id),
            'name': str(node.event_name),
            'start': node.start,
            'end': node.end,
            'max_end': node.max_end,
            'height': node.height,
            'balance': (0 if not node.left else node.left.height) - (0 if not node.right else node.right.height),
            'depth': depth,
            'x': root_x,
            'y': MARGIN_TOP + depth * (CARD_H + V_GAP),
            'card_width': CARD_W,
            'card_height': CARD_H
        }

        sub_nodes = [cur_node] + l_nodes + r_nodes
        sub_edges = []
        if node.left:
            sub_edges.append((node.event_id, node.left.event_id))
        if node.right:
            sub_edges.append((node.event_id, node.right.event_id))
        sub_edges += l_edges + r_edges

        return sub_nodes, sub_edges, total_w, root_x

    sub_nodes, sub_edges, total_w, _ = compute(tree_root)
    canvas_w = max(900, int(total_w + 2 * MARGIN_SIDE))
    offset_x = (canvas_w - total_w) / 2
    for n in sub_nodes:
        n['x'] += offset_x

    max_d = max(n['depth'] for n in sub_nodes) if sub_nodes else 0
    canvas_h = max(400, int(MARGIN_TOP + (max_d + 1) * (CARD_H + V_GAP) + 40))

    return sub_nodes, sub_edges, int(canvas_w), int(canvas_h)


def get_node_statuses(tree_root, trace_rows=None, current_step=0, match_ids=None):
    """
    Categorizes every node into Visited, Skipped, Current, Matching, or Unvisited.
    """
    nodes, _, _, _ = get_tree_nodes_and_positions(tree_root)
    all_ids = {int(item["id"]) for item in nodes}

    visited_ids = set()
    skipped_ids = set()
    matching_ids = set(match_ids) if match_ids else set()
    current_id = None

    trace_rows = trace_rows or []

    for row in trace_rows[:current_step]:
        event_id = row.get("ID")
        if event_id is None:
            continue
        event_id = int(event_id)

        if row.get("Action") == "Visited":
            visited_ids.add(event_id)
        elif str(row.get("Action", "")).startswith("Skipped"):
            skipped_ids.add(event_id)

    if 0 < current_step <= len(trace_rows):
        current_row = trace_rows[current_step - 1]
        c_id = current_row.get("ID")
        if c_id is not None:
            current_id = int(c_id)
            visited_ids.discard(current_id)
            skipped_ids.discard(current_id)

    unvisited_ids = (
        all_ids
        - visited_ids
        - skipped_ids
        - ({current_id} if current_id is not None else set())
    )

    return {
        "Visited": visited_ids,
        "Skipped": skipped_ids,
        "Current": {current_id} if current_id is not None else set(),
        "Matching": matching_ids,
        "Unvisited": unvisited_ids
    }


def render_animated_tree(tree_root, trace_rows=None, current_step=0, filter_status="All", match_ids=None):
    """
    Generates a large, pristine, ultra-readable SVG tree with interactive zoom/pan toolbar,
    safe responsive centering, smooth scrollbars, and zero clipping.
    """
    nodes, edges, width, height = get_tree_nodes_and_positions(tree_root)

    if not nodes:
        return """
        <!DOCTYPE html><html><body style="background:#070B14;color:#94A3B8;font-family:sans-serif;padding:40px;text-align:center;">
        <div style="padding:26px 36px; border:1px dashed #334E68; border-radius:14px; display:inline-block; background:rgba(15,23,42,0.6);">
            <b style="color:#F8FAFC; font-size:16px;">Tree is currently empty</b><br>
            <span style="font-size:13px; color:#94A3B8;">Insert an event to populate the AVL tree.</span>
        </div>
        </body></html>
        """, 220

    statuses = get_node_statuses(tree_root, trace_rows, current_step, match_ids)
    matching_set = set(match_ids) if match_ids else set()

    svg_parts = [
        f'<svg id="tree-svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:block; margin:0 auto; overflow:visible;">'
    ]

    positions = {item["id"]: item for item in nodes}
    half_h = CARD_H / 2  # 48px

    # 1. Draw smooth curved connector branches with glowing gradient
    for parent_id, child_id in edges:
        parent = positions.get(parent_id)
        child = positions.get(child_id)
        if parent and child:
            p_x, p_y = parent["x"], parent["y"] + half_h
            c_x, c_y = child["x"], child["y"] - half_h
            mid_y = (p_y + c_y) / 2
            # Curved connecting branch
            svg_parts.append(
                f'<path class="tree-edge" d="M {p_x} {p_y} C {p_x} {mid_y}, {c_x} {mid_y}, {c_x} {c_y}" />'
            )
            # Connecting dot on child node top
            svg_parts.append(
                f'<circle cx="{c_x}" cy="{c_y}" r="4" fill="#38BDF8" stroke="#060A14" stroke-width="2" />'
            )

    # 2. Draw tree nodes
    for item in nodes:
        event_id = int(item["id"])
        name = html.escape(str(item["name"])[:19])
        interval_str = f'{minutes_to_clock(item["start"])} – {minutes_to_clock(item["end"])}'
        max_end_str = minutes_to_clock(item["max_end"])
        height_val = item["height"]
        bf_val = item["balance"]

        status = "Unvisited"
        if event_id in statuses["Current"]:
            status = "Current"
        elif event_id in matching_set and event_id in statuses["Visited"]:
            status = "Matching"
        elif event_id in statuses["Visited"]:
            status = "Visited"
        elif event_id in statuses["Skipped"]:
            status = "Skipped"

        css_class = {
            "Unvisited": "node-unvisited",
            "Visited": "node-visited",
            "Current": "node-current",
            "Skipped": "node-skipped",
            "Matching": "node-matching"
        }.get(status, "node-unvisited")

        if filter_status != "All":
            if filter_status == "Matching":
                if event_id not in matching_set:
                    css_class += " node-dimmed"
            elif filter_status == "Unvisited":
                if status != "Unvisited":
                    css_class += " node-dimmed"
            elif filter_status == "Visited":
                if status not in ("Visited", "Matching"):
                    css_class += " node-dimmed"
            elif filter_status == "Current":
                if status != "Current":
                    css_class += " node-dimmed"
            elif filter_status == "Skipped":
                if status != "Skipped":
                    css_class += " node-dimmed"

        x, y = item["x"], item["y"]
        card_half_w = CARD_W / 2  # 93px
        card_half_h = CARD_H / 2  # 48px

        svg_parts.append(f"""
        <g class="tree-node {css_class}" transform="translate({x},{y})">
          <!-- Card Background Box -->
          <rect class="card-bg" x="-{card_half_w}" y="-{card_half_h}" width="{CARD_W}" height="{CARD_H}" rx="14"/>
          
          <!-- Top Accent Header Bar -->
          <path d="M -{card_half_w} -26 L -{card_half_w} -36 C -{card_half_w} -42, -{card_half_w - 6} -{card_half_h}, -{card_half_w - 14} -{card_half_h} L {card_half_w - 14} -{card_half_h} C {card_half_w - 6} -{card_half_h}, {card_half_w} -42, {card_half_w} -36 L {card_half_w} -26 Z" class="card-header-bar"/>
          
          <!-- Line 1: Event Name -->
          <text class="node-name" x="0" y="-33">{name}</text>
          
          <!-- Line 2: Event ID -->
          <text class="node-id" x="0" y="-14">ID: #{event_id}</text>
          
          <!-- Line 3: Time Interval -->
          <text class="node-interval" x="0" y="5">⏰ {interval_str}</text>
          
          <!-- Line 4: Height & Balance Factor -->
          <text class="node-meta" x="0" y="22">Height: {height_val} &nbsp;|&nbsp; BF: {bf_val:+d}</text>
          
          <!-- Line 5: Max End in Subtree -->
          <text class="node-max-end" x="0" y="39">Max End: {max_end_str}</text>
        </g>
        """)

    svg_parts.append("</svg>")

    # Calculate optimal container height
    suggested_h = min(max(height + 95, 520), 850)

    document = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap');
  
  * {{ box-sizing: border-box; }}
  
  html, body {{
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    background: #060A14;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;
    overflow: hidden;
  }}
  
  /* Floating Glassmorphism Toolbar */
  .toolbar-wrapper {{
    position: absolute;
    top: 14px;
    left: 18px;
    z-index: 200;
    display: flex;
    align-items: center;
    gap: 7px;
    background: rgba(11, 19, 35, 0.92);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 12px;
    padding: 6px 12px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.55);
  }}
  
  .tool-btn {{
    background: rgba(26, 39, 64, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: #F8FAFC;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}
  
  .tool-btn:hover {{
    background: #1E40AF;
    border-color: #38BDF8;
    color: #FFFFFF;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    transform: translateY(-1px);
  }}
  
  .tool-btn:active {{
    transform: translateY(0);
  }}
  
  .zoom-tag {{
    color: #00F2FE;
    font-size: 11.5px;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    padding: 0 4px;
    min-width: 44px;
    text-align: center;
  }}
  
  /* Scrollable Viewport with zero flexbox negative clipping */
  .viewport {{
    width: 100%;
    height: 100%;
    overflow: auto;
    position: relative;
    cursor: grab;
    scroll-behavior: smooth;
    padding-top: 58px;
    padding-bottom: 20px;
  }}
  
  .viewport:active {{
    cursor: grabbing;
  }}
  
  /* Custom Cyberpunk Scrollbars */
  .viewport::-webkit-scrollbar {{
    width: 10px;
    height: 10px;
  }}
  .viewport::-webkit-scrollbar-track {{
    background: #070D1A;
  }}
  .viewport::-webkit-scrollbar-thumb {{
    background: #1E3A8A;
    border-radius: 5px;
    border: 2px solid #070D1A;
  }}
  .viewport::-webkit-scrollbar-thumb:hover {{
    background: #38BDF8;
  }}
  
  /* Transform container for smooth scaling */
  #pan-container {{
    display: table;
    margin: 0 auto;
    transform-origin: 50% 30px;
    transition: transform 0.12s ease-out;
  }}
  
  /* Curved Branches */
  .tree-edge {{
    fill: none;
    stroke: #334E68;
    stroke-width: 2.8;
    stroke-linecap: round;
    stroke-dasharray: 6 5;
    transition: all 0.3s ease;
  }}
  
  .card-bg {{
    stroke-width: 2.2;
    filter: drop-shadow(0 10px 24px rgba(0,0,0,0.65));
    transition: all 0.25s ease;
  }}
  
  .card-header-bar {{
    fill: rgba(56, 189, 248, 0.14);
  }}
  
  /* Node Status Styles - Exactly as specified in requirements */
  /* Blue = Unvisited */
  .node-unvisited rect.card-bg {{ fill: #0B1323; stroke: #38BDF8; }}
  
  /* Green = Visited */
  .node-visited rect.card-bg {{ fill: #064E3B; stroke: #34D399; }}
  
  /* Cyan / Yellow = Current */
  .node-current rect.card-bg {{
    fill: #082F49;
    stroke: #00F2FE;
    stroke-width: 3.5;
    filter: drop-shadow(0 0 22px rgba(0, 242, 254, 0.95));
    animation: pulseGlow 1.5s infinite;
  }}
  
  /* Red = Skipped */
  .node-skipped rect.card-bg {{ fill: #4C0519; stroke: #FB7185; }}
  
  /* Purple = Matching */
  .node-matching rect.card-bg {{
    fill: #3B0764;
    stroke: #C084FC;
    stroke-width: 3.5;
    filter: drop-shadow(0 0 22px rgba(192, 132, 252, 0.95));
  }}
  
  .node-dimmed {{ opacity: 0.14; }}
  
  /* Crisp Typography */
  .node-name {{
    fill: #FFFFFF;
    font-size: 13px;
    font-weight: 800;
    text-anchor: middle;
    letter-spacing: -0.01em;
  }}
  .node-id {{
    fill: #38BDF8;
    font-size: 11px;
    font-weight: 750;
    text-anchor: middle;
    font-family: 'JetBrains Mono', monospace;
  }}
  .node-interval {{
    fill: #BAE6FD;
    font-size: 11.5px;
    font-weight: 700;
    text-anchor: middle;
  }}
  .node-meta {{
    fill: #94A3B8;
    font-size: 10px;
    font-weight: 600;
    text-anchor: middle;
  }}
  .node-max-end {{
    fill: #00F2FE;
    font-size: 11px;
    font-weight: 800;
    text-anchor: middle;
    font-family: 'JetBrains Mono', monospace;
  }}
  
  @keyframes pulseGlow {{
    0%, 100% {{ filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.5)); }}
    50% {{ filter: drop-shadow(0 0 24px rgba(0, 242, 254, 1.0)); }}
  }}
</style>
</head>
<body>
  <!-- Floating Interactive Toolbar -->
  <div class="toolbar-wrapper">
    <button class="tool-btn" onclick="fitView()">📐 Fit to Screen</button>
    <button class="tool-btn" onclick="resetView()">🔍 100% (Crisp)</button>
    <button class="tool-btn" onclick="zoomIn()">➕ Zoom In</button>
    <button class="tool-btn" onclick="zoomOut()">➖ Zoom Out</button>
    <span class="zoom-tag" id="zoom-label">100%</span>
    <button class="tool-btn" onclick="centerRoot()">🧭 Center View</button>
  </div>

  <!-- Scrollable Canvas Viewport -->
  <div class="viewport" id="viewport">
    <div id="pan-container">
      {''.join(svg_parts)}
    </div>
  </div>

  <script>
    const viewport = document.getElementById('viewport');
    const container = document.getElementById('pan-container');
    const zoomLabel = document.getElementById('zoom-label');
    const svgW = {width};
    const svgH = {height};

    let scale = 1.0;
    let isDragging = false;
    let startX, startY, scrollLeft, scrollTop;

    function updateTransform() {{
      container.style.transform = `scale(${{scale}})`;
      zoomLabel.textContent = Math.round(scale * 100) + '%';
    }}

    function zoomIn() {{
      scale = Math.min(scale * 1.15, 2.5);
      updateTransform();
    }}

    function zoomOut() {{
      scale = Math.max(scale * 0.85, 0.35);
      updateTransform();
    }}

    function resetView() {{
      scale = 1.0;
      updateTransform();
      centerRoot();
    }}

    function fitView() {{
      const availableW = viewport.clientWidth - 48;
      const availableH = viewport.clientHeight - 80;
      if (availableW > 0 && availableH > 0) {{
        scale = Math.min(availableW / svgW, availableH / svgH, 1.0);
        updateTransform();
        viewport.scrollLeft = Math.max(0, (container.offsetWidth * scale - viewport.clientWidth) / 2);
        viewport.scrollTop = 0;
      }}
    }}

    function centerRoot() {{
      setTimeout(() => {{
        const scrollTarget = (container.offsetWidth * scale - viewport.clientWidth) / 2;
        viewport.scrollLeft = Math.max(0, scrollTarget);
        viewport.scrollTop = 0;
      }}, 50);
    }}

    // Mouse Drag Panning on canvas
    viewport.addEventListener('mousedown', (e) => {{
      if (e.target.closest('.toolbar-wrapper')) return;
      isDragging = true;
      startX = e.pageX - viewport.offsetLeft;
      startY = e.pageY - viewport.offsetTop;
      scrollLeft = viewport.scrollLeft;
      scrollTop = viewport.scrollTop;
    }});

    window.addEventListener('mousemove', (e) => {{
      if (!isDragging) return;
      e.preventDefault();
      const x = e.pageX - viewport.offsetLeft;
      const y = e.pageY - viewport.offsetTop;
      const walkX = (x - startX) * 1.2;
      const walkY = (y - startY) * 1.2;
      viewport.scrollLeft = scrollLeft - walkX;
      viewport.scrollTop = scrollTop - walkY;
    }});

    window.addEventListener('mouseup', () => {{
      isDragging = false;
    }});

    // Mouse Wheel Zooming
    viewport.addEventListener('wheel', (e) => {{
      if (e.ctrlKey) {{
        e.preventDefault();
        if (e.deltaY < 0) zoomIn();
        else zoomOut();
      }}
    }}, {{ passive: false }});

    // Smart Auto-Fit on load if tree is wide
    window.addEventListener('load', () => {{
      if (svgW > viewport.clientWidth - 40) {{
        fitView();
      }} else {{
        centerRoot();
      }}
    }});
  </script>
</body>
</html>"""

    return document, suggested_h


def insert_with_rotations(root, new_node):
    """
    Inserts a node into the AVL tree using the exact algorithm from avl_interval_tree.py,
    recording any LL, RR, LR, or RL rotations that occur.
    Returns: (new_root, list_of_rotation_events)
    """
    rotation_events = []

    def _insert(curr):
        if curr is None:
            return new_node

        key = (new_node.start, new_node.event_id)
        root_key = (curr.start, curr.event_id)

        if key < root_key:
            curr.left = _insert(curr.left)
        else:
            curr.right = _insert(curr.right)

        update(curr)
        balance = get_balance(curr)

        # 1. Left-Heavy Imbalance (LL or LR)
        if balance > 1:
            left_key = (curr.left.start, curr.left.event_id)
            if key < left_key:
                # LL Rotation: Right rotate curr
                before_tree = copy.deepcopy(curr)
                rotated = right_rotate(curr)
                after_tree = copy.deepcopy(rotated)
                rotation_events.append({
                    "type": "LL Rotation",
                    "operation": "Single Right Rotation",
                    "pivot_id": curr.event_id,
                    "pivot_name": curr.event_name,
                    "balance_factor": balance,
                    "inserted_id": new_node.event_id,
                    "inserted_name": new_node.event_name,
                    "before_tree": before_tree,
                    "after_tree": after_tree,
                    "reason": f"Node '{curr.event_name}' (ID #{curr.event_id}) became left-heavy (Balance Factor = +{balance}) after inserting '{new_node.event_name}' (ID #{new_node.event_id}) into its left subtree. A single Right Rotation on '{curr.event_name}' rebalances the tree."
                })
                return rotated
            else:
                # LR Rotation: Left rotate left child, then Right rotate curr
                before_tree = copy.deepcopy(curr)
                curr.left = left_rotate(curr.left)
                rotated = right_rotate(curr)
                after_tree = copy.deepcopy(rotated)
                rotation_events.append({
                    "type": "LR Rotation",
                    "operation": "Left Rotate child, then Right Rotate root",
                    "pivot_id": curr.event_id,
                    "pivot_name": curr.event_name,
                    "balance_factor": balance,
                    "inserted_id": new_node.event_id,
                    "inserted_name": new_node.event_name,
                    "before_tree": before_tree,
                    "after_tree": after_tree,
                    "reason": f"Node '{curr.event_name}' (ID #{curr.event_id}) became left-heavy (Balance Factor = +{balance}) with a right-leaning left child. A Left Rotation on child '{curr.left.event_name}' followed by a Right Rotation on '{curr.event_name}' rebalances the tree."
                })
                return rotated

        # 2. Right-Heavy Imbalance (RR or RL)
        if balance < -1:
            right_key = (curr.right.start, curr.right.event_id)
            if key > right_key:
                # RR Rotation: Left rotate curr
                before_tree = copy.deepcopy(curr)
                rotated = left_rotate(curr)
                after_tree = copy.deepcopy(rotated)
                rotation_events.append({
                    "type": "RR Rotation",
                    "operation": "Single Left Rotation",
                    "pivot_id": curr.event_id,
                    "pivot_name": curr.event_name,
                    "balance_factor": balance,
                    "inserted_id": new_node.event_id,
                    "inserted_name": new_node.event_name,
                    "before_tree": before_tree,
                    "after_tree": after_tree,
                    "reason": f"Node '{curr.event_name}' (ID #{curr.event_id}) became right-heavy (Balance Factor = {balance}) after inserting '{new_node.event_name}' (ID #{new_node.event_id}) into its right subtree. A single Left Rotation on '{curr.event_name}' rebalances the tree."
                })
                return rotated
            else:
                # RL Rotation: Right rotate right child, then Left rotate curr
                before_tree = copy.deepcopy(curr)
                curr.right = right_rotate(curr.right)
                rotated = left_rotate(curr)
                after_tree = copy.deepcopy(rotated)
                rotation_events.append({
                    "type": "RL Rotation",
                    "operation": "Right Rotate child, then Left Rotate root",
                    "pivot_id": curr.event_id,
                    "pivot_name": curr.event_name,
                    "balance_factor": balance,
                    "inserted_id": new_node.event_id,
                    "inserted_name": new_node.event_name,
                    "before_tree": before_tree,
                    "after_tree": after_tree,
                    "reason": f"Node '{curr.event_name}' (ID #{curr.event_id}) became right-heavy (Balance Factor = {balance}) with a left-leaning right child. A Right Rotation on child '{curr.right.event_name}' followed by a Left Rotation on '{curr.event_name}' rebalances the tree."
                })
                return rotated

        return curr

    new_root = _insert(root)
    return new_root, rotation_events


def make_insertion_snapshots(dataframe):
    """
    Builds incremental tree snapshots after each event insertion, tracking:
    - Step index
    - Inserted event metadata
    - Rebalanced tree state
    - Any AVL rotations (LL, RR, LR, RL) triggered on that step
    """
    snapshots = []
    working_root = None

    ordered = dataframe.sort_values(
        by=["start_time", "event_id"]
    ).reset_index(drop=True)

    for idx, event in ordered.iterrows():
        new_node = Node(
            int(event["event_id"]),
            str(event["event_name"]),
            to_minutes(event["start_time"]),
            to_minutes(event["end_time"])
        )

        working_root, rotations = insert_with_rotations(working_root, new_node)

        snapshots.append({
            "step": idx + 1,
            "event": event,
            "tree": copy.deepcopy(working_root),
            "rotations": rotations
        })

    return snapshots, ordered
