
import pandas as pd
from pathlib import Path

from avl_interval_tree import Node, insert, delete, search_overlaps


def to_minutes(time):
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


# Load events
file_path = Path(__file__).with_name("events.csv")
events = pd.read_csv(file_path)

# Build AVL tree
root = None

for _, event in events.iterrows():
    node = Node(
        int(event["event_id"]),
        event["event_name"],
        to_minutes(event["start_time"]),
        to_minutes(event["end_time"])
    )
    root = insert(root, node)

print("BEFORE DELETION")
print("----------------")

results = []
search_overlaps(root, 10 * 60, 11 * 60, results)

for event in results:
    print(event.event_name)

print("Total events:", len(results))


# Delete Workshop (event ID 2, start time 10:00)
root = delete(root, 10 * 60, 2)

print("\nAFTER DELETION")
print("---------------")

results = []
search_overlaps(root, 10 * 60, 11 * 60, results)

for event in results:
    print(event.event_name)

print("Total events:", len(results))
