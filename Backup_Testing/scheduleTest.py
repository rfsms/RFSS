import datetime
import time
import pytz

def your_function(label):
    # Your function's code here
    print(f"Function with label '{label}' is running!")

# List of days and times when the function should run in UTC, with labels
schedule = [
    (1,"(3, 16, 22)","(3, 31, 8)","METOP-B"),   # Monday, 10:00:00 - 10:20:00 UTC
    (4, (18, 48, 0), (18, 48, 30), "item2"),  # Wednesday, 15:30:00 - 15:50:00 UTC
    (4, (18, 48, 20), (18, 49, 0), "item3"),   # Friday, 12:00:00 - 12:20:00 UTC
    # (4, (16, 56, 0), (16, 57, 0), "item4"),  # Thursday, 16:56:00 - 16:57:00 UTC
    # (4, (16, 56, 50), (16, 57, 30), "item5"),# Thursday, 16:56:50 - 16:57:30 UTC
    # Add more entries for other days and times in UTC
]

# Convert the schedule times to UTC timezone and sort by start time
utc = pytz.UTC
utc_schedule = sorted(
    [(day, datetime.time(hour, minute, second), datetime.time(end_hour, end_minute, end_second), label) for day, (hour, minute, second), (end_hour, end_minute, end_second), label in schedule],
    key=lambda entry: entry[1]  # Sort by start_time (entry[1])
)

while True:
    now = datetime.datetime.now(tz=utc)
    current_day = now.weekday()

    for day, start_time, end_time, label in utc_schedule:
        if current_day == day:
            if start_time <= now.time() <= end_time:
                # Execute your function here with the corresponding label
                your_function(label)
                break  # Stop checking other entries for this minute

    # Print current time in UTC
    print("Current time (UTC):", now)

    # Wait for 1 minute before checking again
    time.sleep(1)
