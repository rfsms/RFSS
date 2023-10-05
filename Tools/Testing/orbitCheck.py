from skyfield.api import Topos, load
import numpy as np
from datetime import datetime

# Load satellite TLE data
stations_url = 'http://celestrak.com/NORAD/elements/weather.txt'
satellites = load.tle_file(stations_url, filename='/home/noaa_gms/RFSS/Tools/Report_Exports/weather.txt')
by_name = {sat.name: sat for sat in satellites}
all_passes = []

# Define observer location (latitude, longitude, elevation) - in this case TMTR Boulder, CO
observer = Topos(latitude_degrees=40.131142, longitude_degrees=-105.240288, elevation_m=1693)

from datetime import datetime

# Get current date for use
current_date = datetime.now().date()
# # Manually set the specific date you want to look at
# current_date = datetime.strptime("2023-08-29", "%Y-%m-%d").date()

# Load time scale and generate time array
ts = load.timescale()
t0 = ts.utc(current_date.year, current_date.month, current_date.day, 0, 0)
t1 = ts.utc(current_date.year, current_date.month, current_date.day + 1, 0, 0)
times = ts.utc(current_date.year, current_date.month, current_date.day, np.linspace(0, 24, 10000))

satellite_names = ["NOAA 18", "NOAA 19", "METOP-B", "METOP-C"]

for sat_name in satellite_names:
    satellite = by_name[sat_name]
    
    # Calculate satellite's position
    astrometric = (satellite - observer).at(times)
    alt, az, d = astrometric.altaz()

    # Find AOS and LOS above 5*
    above_horizon = alt.degrees > 5
    diff = np.diff(above_horizon.astype(int))

    aos_times = times[:-1][diff > 0]
    los_times = times[:-1][diff < 0]
    
    for i in range(len(aos_times)):
        aos = aos_times[i].tt
        los = los_times[i].tt
        mask = (times.tt >= aos) & (times.tt <= los)
        pass_alt = alt.degrees[mask]

        if len(pass_alt) > 0:
            max_elevation = round(np.max(pass_alt), 2)
            aos_datetime = aos_times[i].utc_iso()
            los_datetime = los_times[i].utc_iso()
            
            # Calculate interval between AOS and LOS
            aos_dt = datetime.fromisoformat(aos_datetime.replace("Z", "+00:00"))
            los_dt = datetime.fromisoformat(los_datetime.replace("Z", "+00:00"))
            interval = los_dt - aos_dt
            
            all_passes.append((sat_name, aos_datetime, los_datetime, max_elevation, interval))


all_passes.sort(key=lambda x: x[1])

# Print sorted list with row number and in desired format
print("Pass,DayofWeek,AOS,LOS,Satellite,MaxElevation")
for idx, (sat_name, aos, los, max_el, interval) in enumerate(all_passes, 1):
    aos_dt = datetime.fromisoformat(aos.replace("Z", "+00:00"))
    los_dt = datetime.fromisoformat(los.replace("Z", "+00:00"))
    day_of_week = aos_dt.weekday()

    aos_time = f'({aos_dt.hour},{aos_dt.minute},{aos_dt.second})'
    los_time = f'({los_dt.hour},{los_dt.minute},{los_dt.second})'

    print(f"{idx},{day_of_week},{aos_time},{los_time},{sat_name.replace(' ', '-')},{max_el}")





# stations_url = 'http://www.csntechnologies.net/SAT/weather.txt'
# Pass,DayofWeek,AOS,LOS,Satellite,MaxElevation
# 1,0,(1,41,58),(1,51,28),NOAA-19,16.16
# 2,0,(2,21,17),(2,29,55),METOP-B,13.51
# 3,0,(3,11,41),(3,23,38),METOP-C,36.96
# 4,0,(3,20,11),(3,33,17),NOAA-19,70.8
# 5,0,(3,47,33),(3,58,38),NOAA-18,23.1
# 6,0,(3,58,29),(4,11,18),METOP-B,82.35
# 7,0,(4,52,4),(5,3,35),METOP-C,27.33
# 8,0,(5,5,45),(5,10,47),NOAA-19,7.09
# 9,0,(5,26,55),(5,39,52),NOAA-18,48.65
# 10,0,(5,42,28),(5,49,5),METOP-B,8.82
# 11,0,(15,30,11),(15,39,33),METOP-C,15.0
# 12,0,(15,42,34),(15,55,23),NOAA-19,51.86
# 13,0,(16,10,57),(16,17,8),NOAA-18,8.22
# 14,0,(16,16,25),(16,28,48),METOP-B,41.75
# 15,0,(17,8,59),(17,21,39),METOP-C,65.73
# 16,0,(17,23,49),(17,34,37),NOAA-19,21.71
# 17,0,(17,49,1),(18,1,59),NOAA-18,77.48
# 18,0,(17,56,56),(18,8,2),METOP-B,24.96
# 19,0,(18,51,23),(18,57,26),METOP-C,8.47
# 20,0,(19,30,50),(19,40,3),NOAA-18,14.81

# stations_url = 'http://celestrak.com/NORAD/elements/weather.txt'
# Pass,DayofWeek,AOS,LOS,Satellite,MaxElevation
# 1,0,(1,41,58),(1,51,28),NOAA-19,16.16
# 2,0,(2,21,17),(2,29,55),METOP-B,13.51
# 3,0,(3,11,41),(3,23,38),METOP-C,36.96
# 4,0,(3,20,11),(3,33,17),NOAA-19,70.8
# 5,0,(3,47,33),(3,58,38),NOAA-18,23.1
# 6,0,(3,58,29),(4,11,18),METOP-B,82.35
# 7,0,(4,52,4),(5,3,35),METOP-C,27.33
# 8,0,(5,5,45),(5,10,47),NOAA-19,7.09
# 9,0,(5,26,55),(5,39,52),NOAA-18,48.65
# 10,0,(5,42,28),(5,49,5),METOP-B,8.82
# 11,0,(15,30,11),(15,39,33),METOP-C,15.0
# 12,0,(15,42,34),(15,55,23),NOAA-19,51.86
# 13,0,(16,10,57),(16,17,8),NOAA-18,8.22
# 14,0,(16,16,25),(16,28,48),METOP-B,41.75
# 15,0,(17,8,59),(17,21,39),METOP-C,65.73
# 16,0,(17,23,49),(17,34,37),NOAA-19,21.71
# 17,0,(17,49,1),(18,1,59),NOAA-18,77.48
# 18,0,(17,56,56),(18,8,2),METOP-B,24.96
# 19,0,(18,51,23),(18,57,26),METOP-C,8.47
# 20,0,(19,30,50),(19,40,3),NOAA-18,14.81

# https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle
# [#################################] 100% gp.php
# Pass,DayofWeek,AOS,LOS,Satellite,MaxElevation
# 1,0,(1,41,58),(1,51,28),NOAA-19,16.16
# 2,0,(2,21,17),(2,29,55),METOP-B,13.51
# 3,0,(3,11,41),(3,23,38),METOP-C,36.96
# 4,0,(3,20,11),(3,33,17),NOAA-19,70.8
# 5,0,(3,47,33),(3,58,38),NOAA-18,23.1
# 6,0,(3,58,29),(4,11,18),METOP-B,82.35
# 7,0,(4,52,4),(5,3,35),METOP-C,27.33
# 8,0,(5,5,45),(5,10,47),NOAA-19,7.09
# 9,0,(5,26,55),(5,39,52),NOAA-18,48.65
# 10,0,(5,42,28),(5,49,5),METOP-B,8.82
# 11,0,(15,30,11),(15,39,33),METOP-C,15.0
# 12,0,(15,42,34),(15,55,23),NOAA-19,51.86
# 13,0,(16,10,57),(16,17,8),NOAA-18,8.22
# 14,0,(16,16,25),(16,28,48),METOP-B,41.75
# 15,0,(17,8,59),(17,21,39),METOP-C,65.73
# 16,0,(17,23,49),(17,34,37),NOAA-19,21.71
# 17,0,(17,49,1),(18,1,59),NOAA-18,77.48
# 18,0,(17,56,56),(18,8,2),METOP-B,24.96
# 19,0,(18,51,23),(18,57,26),METOP-C,8.47
# 20,0,(19,30,50),(19,40,3),NOAA-18,14.81