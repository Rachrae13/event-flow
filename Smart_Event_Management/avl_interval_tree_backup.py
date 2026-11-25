
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
    if node is None:
        return 0
    return node.height


def update(node):
    if node is not None:
        node.height = 1 + max(height(node.left), height(node.right))

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
        else:
            root.left = left_rotate(root.left)
            return right_rotate(root)

    if balance < -1:
        if (new_node.start, new_node.event_id) > (
            root.right.start, root.right.event_id
        ):
            return left_rotate(root)
        else:
            root.right = right_rotate(root.right)
            return left_rotate(root)

    return root



def search_overlaps(root, query_start, query_end, results, trace=None):
    if trace is not None:
        if root is None:
            return

        trace.append({
            "Event": root.event_name,
            "Start": root.start,
            "End": root.end,
            "Max End": root.max_end,
            "Action": "Visited"
        })

    if root is None:
        return

    if root.start < query_end and query_start < root.end:
        results.append(root)

    if root.left and root.left.max_end > query_start:
        search_overlaps(
            root.left, query_start, query_end, results, trace
        )
    elif trace is not None and root.left:
        trace.append({
            "Event": root.left.event_name,
            "Start": root.left.start,
            "End": root.left.end,
            "Max End": root.left.max_end,
            "Action": "Skipped - Max End too early"
        })

    if root.right and root.start < query_end:
        search_overlaps(
            root.right, query_start, query_end, results, trace
        )
    elif trace is not None and root.right:
        trace.append({
            "Event": root.right.event_name,
            "Start": root.right.start,
            "End": root.right.end,
            "Max End": root.right.max_end,
            "Action": "Skipped - Start too late"
        })

    if root is None:
        return

    if root.start < query_end and query_start < root.end:
        results.append(root)

    if root.left and root.left.max_end > query_start:
        search_overlaps(root.left, query_start, query_end, results)

    if root.right and root.start < query_end:
        search_overlaps(root.right, query_start, query_end, results)

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
        else:
            root.left = left_rotate(root.left)
            return right_rotate(root)

    if balance < -1:
        if get_balance(root.right) <= 0:
            return left_rotate(root)
        else:
            root.right = right_rotate(root.right)
            return left_rotate(root)

    return root
