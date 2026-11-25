
class Node:
    def __init__(self, event_id, event_name, start, end):
        self.event_id = event_id
        self.event_name = event_name
        self.start = start
        self.end = end
        self.max_end = end
        self.height = 1
        self.left = None
        self.right = None


def height(node):
    return 0 if node is None else node.height


def update(node):
    if node is not None:
        node.height = 1 + max(
            height(node.left),
            height(node.right)
        )

        node.max_end = node.end

        if node.left:
            node.max_end = max(node.max_end, node.left.max_end)

        if node.right:
            node.max_end = max(node.max_end, node.right.max_end)


def right_rotate(y):
    x = y.left
    temp = x.right

    x.right = y
    y.left = temp

    update(y)
    update(x)

    return x


def left_rotate(x):
    y = x.right
    temp = y.left

    y.left = x
    x.right = temp

    update(x)
    update(y)

    return y


def get_balance(node):
    if node is None:
        return 0

    return height(node.left) - height(node.right)


def insert(root, new_node):
    if root is None:
        return new_node

    key = (new_node.start, new_node.event_id)
    root_key = (root.start, root.event_id)

    if key < root_key:
        root.left = insert(root.left, new_node)
    else:
        root.right = insert(root.right, new_node)

    update(root)

    balance = get_balance(root)

    if balance > 1:
        if (new_node.start, new_node.event_id) < (
            root.left.start, root.left.event_id
        ):
            return right_rotate(root)

        root.left = left_rotate(root.left)
        return right_rotate(root)

    if balance < -1:
        if (new_node.start, new_node.event_id) > (
            root.right.start, root.right.event_id
        ):
            return left_rotate(root)

        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root


def record_skipped_subtree(node, trace, reason):
    """
    Record every node in a pruned subtree.
    Event IDs allow accurate visual highlighting.
    """

    if node is None or trace is None:
        return

    trace.append({
        "ID": node.event_id,
        "Event": node.event_name,
        "Start": node.start,
        "End": node.end,
        "Max End": node.max_end,
        "Action": reason
    })

    record_skipped_subtree(node.left, trace, reason)
    record_skipped_subtree(node.right, trace, reason)


def search_overlaps(root, query_start, query_end, results, trace=None):
    """
    Search for overlapping intervals.

    Overlap condition:
        event.start < query_end
        AND query_start < event.end

    Trace actions:
        Visited
        Skipped - Max End too early
        Skipped - Start too late
    """

    if root is None:
        return

    if trace is not None:
        trace.append({
            "ID": root.event_id,
            "Event": root.event_name,
            "Start": root.start,
            "End": root.end,
            "Max End": root.max_end,
            "Action": "Visited"
        })

    if root.start < query_end and query_start < root.end:
        results.append(root)

    # Explore left subtree only if it may contain an overlap.
    if root.left:

        if root.left.max_end > query_start:
            search_overlaps(
                root.left,
                query_start,
                query_end,
                results,
                trace
            )

        elif trace is not None:
            record_skipped_subtree(
                root.left,
                trace,
                "Skipped - Max End too early"
            )

    # Explore right subtree only if it may contain an overlap.
    if root.right:

        if root.start < query_end:
            search_overlaps(
                root.right,
                query_start,
                query_end,
                results,
                trace
            )

        elif trace is not None:
            record_skipped_subtree(
                root.right,
                trace,
                "Skipped - Start too late"
            )


def minimum_node(node):
    current = node

    while current.left is not None:
        current = current.left

    return current


def delete(root, start, event_id):
    if root is None:
        return None

    key = (start, event_id)
    root_key = (root.start, root.event_id)

    if key < root_key:
        root.left = delete(root.left, start, event_id)

    elif key > root_key:
        root.right = delete(root.right, start, event_id)

    else:

        if root.left is None:
            return root.right

        elif root.right is None:
            return root.left

        successor = minimum_node(root.right)

        root.event_id = successor.event_id
        root.event_name = successor.event_name
        root.start = successor.start
        root.end = successor.end

        root.right = delete(
            root.right,
            successor.start,
            successor.event_id
        )

    update(root)

    balance = get_balance(root)

    if balance > 1:
        if get_balance(root.left) >= 0:
            return right_rotate(root)

        root.left = left_rotate(root.left)
        return right_rotate(root)

    if balance < -1:
        if get_balance(root.right) <= 0:
            return left_rotate(root)

        root.right = right_rotate(root.right)
        return left_rotate(root)

    return root
