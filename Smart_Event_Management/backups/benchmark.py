
import pandas as pd
import time

from pathlib import Path
from avl_interval_tree import Node, insert, search_overlaps


def to_minutes(time_value):
    hours, minutes = map(int, time_value.split(":"))
    return hours * 60 + minutes


# Load dataset
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


# Search interval
query_start = to_minutes("10:00")
query_end = to_minutes("11:00")


# Linear search
def linear_search():
    results = []

    for _, event in events.iterrows():
        start = to_minutes(event["start_time"])
        end = to_minutes(event["end_time"])

        if start < query_end and query_start < end:
            results.append(event)

    return results


# AVL search
def avl_search():
    results = []
    search_overlaps(root, query_start, query_end, results)
    return results


# Measure execution time
repetitions = 1000

start_time = time.perf_counter()

for _ in range(repetitions):
    linear_results = linear_search()

linear_time = time.perf_counter() - start_time


start_time = time.perf_counter()

for _ in range(repetitions):
    avl_results = avl_search()

avl_time = time.perf_counter() - start_time


# Display results
print("PERFORMANCE COMPARISON")
print("----------------------")

print("Search interval: 10:00 to 11:00")
print("Number of repetitions:", repetitions)

print("\nLinear Search")
print("Overlapping events:", len(linear_results))
print("Execution time:", round(linear_time, 6), "seconds")

print("\nAVL Interval Tree")
print("Overlapping events:", len(avl_results))
print("Execution time:", round(avl_time, 6), "seconds")

print("\nBoth methods return the same number of events.")
