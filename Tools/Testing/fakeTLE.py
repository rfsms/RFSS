from skyfield.api import Topos, load
from skyfield.api import EarthSatellite
from datetime import datetime, timedelta

# Your location
latitude = 38.7577891891954
longitude = -77.36191490392743
location = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

# Define the TLE lines
tle_lines = [
    '1 99999U 21275A   23001.00000000  .00000000  00000-0  00000-0 0  9991',
    '2 99999  98.0000   0.0000 0000001   0.0000   0.0000 10.0000000000010'
]

# Create a satellite object
satellite = EarthSatellite(tle_lines[0], tle_lines[1], 'FAKE SAT', load.timescale())

# Use the current time as the start time
start_time = datetime.utcnow()
end_time = start_time + timedelta(days=1)  # Predict passes for the next day

# Find events for the next 24 hours
ts = load.timescale()
t0 = ts.utc(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, start_time.second)
t1 = ts.utc(end_time.year, end_time.month, end_time.day, end_time.hour, end_time.minute, end_time.second)

# Get the times when the satellite is above the horizon
t, events = satellite.find_events(location, t0, t1, altitude_degrees=30.0)

# Output the results
for ti, event in zip(t, events):
    name = ('rise', 'culminate', 'set')[event]
    print(f"{ti.utc_datetime()} {name}")

