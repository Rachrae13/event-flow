
import pandas as pd
from pathlib import Path

file_path = Path(__file__).with_name("events.csv")
events = pd.read_csv(file_path)

def to_minutes(time):
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes

def linear_interval_search(events, query_start, query_end):
    result = []

    for _, event in events.iterrows():
        event_start = to_minutes(event["start_time"])
        event_end = to_minutes(event["end_time"])

        if event_start < query_end and query_start < event_end:
            result.append(event)

    return result

print("SMART EVENT AND INTERVAL QUERY MANAGEMENT")
print("------------------------------------------")

start_time = input("Enter start time (HH:MM): ")
end_time = input("Enter end time (HH:MM): ")

start = to_minutes(start_time)
end = to_minutes(end_time)

if start >= end:
    print("Invalid interval! End time must be after start time.")
else:
    matches = linear_interval_search(events, start, end)

    print("\nOVERLAPPING EVENTS:")
    for event in matches:
        print(
            event["event_name"],
            "|",
            event["start_time"],
            "-",
            event["end_time"]
        )

    print("\nTotal overlapping events:", len(matches))
