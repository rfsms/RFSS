import requests
import time
import asciichartpy
from collections import deque
from datetime import datetime

def print_timestamps(length, start_time, interval_seconds):
    timestamps = [start_time + i * interval_seconds for i in range(length)]
    formatted_timestamps = [datetime.fromtimestamp(ts).strftime('%H:%M') for ts in timestamps]
    step = max(length // 10, 1)  # Ensure step is at least 1
    labels = [formatted_timestamps[i] if i % step == 0 else '' for i in range(length)]
    print(' '.join(labels))

# Initialize deque with a fixed size corresponding to 48 hours (assuming 5-second intervals)
window_size = 48 * 60 * 60 // 5
az_values = deque(maxlen=window_size)
el_values = deque(maxlen=window_size)
timestamps = deque(maxlen=window_size)

# Function to fetch and display data every 5 seconds
def fetch_data():
    while True:
        # Making a GET request to the URL
        response = requests.get('http://192.168.4.1/status')
        data = response.json()

        # Extracting relevant data
        az = data['az']
        el = data['el']
        time_val = data['time']

        # Appending new values to the deques
        az_values.append(az)
        el_values.append(el)
        timestamps.append(time_val)

        # Clear the terminal
        print('\033[H\033[J')

        # Print the ASCII charts
        print("Azimuth:")
        print(asciichartpy.plot(list(az_values), {'height': 10}))
        print_timestamps(len(az_values), timestamps[0] if timestamps else time_val, 5)
        print("\nElevation:")
        print(asciichartpy.plot(list(el_values), {'height': 10}))
        print_timestamps(len(el_values), timestamps[0] if timestamps else time_val, 5)

        # Wait for 5 seconds
        time.sleep(5)

# Start fetching data
fetch_data()
