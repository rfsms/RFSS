import http.client
import time
import json

# Takes about 55s for full 360* azmuthal rotation ~7*/s.  
# Takes about 66s for a full 180* elevated rise ~3*/s.
# Target azimuth and elevation
target_az = 0
target_el = 0

# Tolerance value
tolerance = 1

def get_current_azimuth(conn):
    conn.request("GET", "/track")
    response = conn.getresponse()
    data = json.loads(response.read())
    response.close()
    return round(data['az'], 2), round(data['el'], 2)

def within_tolerance(value, target, tolerance):
    return target - tolerance <= value <= target + tolerance

while True:
    current_az, current_el = get_current_azimuth(conn)
    print(f"Azimuth: {current_az}, Elevation: {current_el}")
    if within_tolerance(current_az, target_az, tolerance) and within_tolerance(current_el, target_el, tolerance):
        break
    time.sleep(1)  # Polling interval




# Connect to the server
conn = http.client.HTTPConnection("192.168.4.1", 80)

# Send GET request to set the target azimuth and elevation
conn.request("GET", f"/cmd?a=P|{target_az}|{target_el}|")
response = conn.getresponse()
response.read()
response.close()

# Record the start time
start_time = time.time()



# # Loop through each target azimuth in 5-degree increments
# for target_az in range(0, 361, 5):
#     # Send GET request to set the target azimuth and elevation
#     conn.request("GET", f"/cmd?a=P|{target_az}|{target_el}|")
#     response = conn.getresponse()
#     response.read()
#     response.close()

#     # Poll the current azimuth and elevation until they reach the target within the tolerance
#     while True:
#         current_az, current_el = get_current_azimuth(conn)
#         print(f"Azimuth: {current_az}, Elevation: {current_el}")
#         if within_tolerance(current_az, target_az, tolerance) and within_tolerance(current_el, target_el, tolerance):
#             break
#         time.sleep(1)  # Polling interval

# Poll the current azimuth and elevation until it reaches the target within the tolerance
# Remove if using for loop to send 5* increments on AZ
while True:
    current_az, current_el = get_current_azimuth(conn)
    print(f"Azimuth: {current_az}, Elevation: {current_el}")
    if within_tolerance(current_az, target_az, tolerance) and within_tolerance(current_el, target_el, tolerance):
        break
    time.sleep(1)  # Polling interval

# Record the end time
end_time = time.time()

# Calculate the time taken
time_taken = end_time - start_time

print(f"Time taken: {time_taken} seconds")
