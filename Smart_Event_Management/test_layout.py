from components.data_loader import load_unified_events
from components.tree_renderer import make_insertion_snapshots

df, _, _, _ = load_unified_events()
snaps, _ = make_insertion_snapshots(df)

card_w = 172
card_h = 92
h_gap = 26
v_gap = 70
margin_top = 65
margin_side = 50

def layout_tree(root):
    def compute(node, depth=0):
        if not node:
            return [], [], 0, 0
        
        l_nodes, l_edges, l_w, l_rx = compute(node.left, depth + 1)
        r_nodes, r_edges, r_w, r_rx = compute(node.right, depth + 1)
        
        if l_w > 0 and r_w > 0:
            r_shift = l_w + h_gap
            for rn in r_nodes:
                rn['x'] += r_shift
            root_x = (l_rx + r_rx + r_shift) / 2
            total_w = l_w + h_gap + r_w
        elif l_w > 0:
            root_x = l_w
            total_w = l_w + card_w / 2
        elif r_w > 0:
            root_x = card_w / 2
            r_shift = card_w / 2 + h_gap
            for rn in r_nodes:
                rn['x'] += r_shift
            total_w = r_shift + r_w
        else:
            root_x = card_w / 2
            total_w = card_w
        
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
            'y': margin_top + depth * (card_h + v_gap)
        }
        
        sub_nodes = [cur_node] + l_nodes + r_nodes
        sub_edges = []
        if node.left:
            sub_edges.append((node.event_id, node.left.event_id))
        if node.right:
            sub_edges.append((node.event_id, node.right.event_id))
        sub_edges += l_edges + r_edges
        
        return sub_nodes, sub_edges, total_w, root_x

    sub_nodes, sub_edges, total_w, root_x = compute(root)
    canvas_w = max(860, int(total_w + 2 * margin_side))
    offset_x = (canvas_w - total_w) / 2
    for n in sub_nodes:
        n['x'] += offset_x
    
    max_d = max(n['depth'] for n in sub_nodes) if sub_nodes else 0
    canvas_h = max(360, int(margin_top + (max_d + 1) * (card_h + v_gap) + 40))
    return sub_nodes, sub_edges, canvas_w, canvas_h

for step in [1, 2, 3, 5, 10, 15]:
    sn = snaps[step - 1]
    nlist, elist, cw, ch = layout_tree(sn['tree'])
    print(f"Step {step}: {len(nlist)} nodes, Canvas={cw}x{ch}, Root X={nlist[0]['x']:.1f}, Y={nlist[0]['y']}")
    # Check bounding box
    min_x = min(n['x'] for n in nlist)
    max_x = max(n['x'] for n in nlist)
    assert min_x - card_w/2 >= 0, f"Left boundary violation at step {step}: {min_x - card_w/2}"
    assert max_x + card_w/2 <= cw, f"Right boundary violation at step {step}: {max_x + card_w/2} > {cw}"
print("ALL BOUNDING BOXES VERIFIED PERFECTLY!")
