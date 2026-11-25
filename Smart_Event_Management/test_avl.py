
import pandas as pd
from pathlib import Path

from avl_interval_tree import Node, insert, search_overlaps


def to_minutes(time):
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


# Read event dataset
file_path = Path(__file__).with_name("events.csv")
events = pd.read_csv(file_path)

# Create AVL tree
root = None

for _, event in events.iterrows():

    start = to_minutes(event["start_time"])
    end = to_minutes(event["end_time"])

    new_node = Node(
        int(event["event_id"]),
        event["event_name"],
        start,
        end
    )

    root = insert(root, new_node)


print("AVL INTERVAL TREE SEARCH")
print("------------------------")

query_start = input("Enter start time (HH:MM): ")
query_end = input("Enter end time (HH:MM): ")

start = to_minutes(query_start)
end = to_minutes(query_end)

if start >= end:

    print("Invalid interval! End time must be after start time.")

else:

    results = []
    trace = []

    search_overlaps(
        root,
        start,
        end,
        results,
        trace
    )

    print("\nOVERLAPPING EVENTS")
    print("------------------")

    for event in results:

        print(
            event.event_name,
            "|",
            f"{event.start // 60:02d}:{event.start % 60:02d}",
            "-",
            f"{event.end // 60:02d}:{event.end % 60:02d}"
        )

    print("\nTOTAL CONFLICTS:", len(results))

    print("\nAVL SEARCH ANIMATION TRACE")
    print("--------------------------")

    for index, step in enumerate(trace, start=1):

        print(
            index,
            "|",
            step["Event"],
            "|",
            step["Action"]
        )

    print("\nTotal nodes in search trace:", len(trace))
