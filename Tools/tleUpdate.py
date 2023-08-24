#!/usr/bin/env python3
# This tool provides capabilities to douwnload the CSN weather TLE since SATTracker may not have access to
# the internet. This is done weekly at Sat 23:59 as a cron job (50 23 * * 6 /usr/bin/python3 /home/noaa_gms/RFSS/Tools/tleUpdate.py)
# Once downloaded, this script  uploads to the SATTracker for use.
import requests
import os

# Define the directory path where the file will be saved
path = '/home/noaa_gms/RFSS/Tools'

# Perform a GET request to download the file
get_url = 'http://www.csntechnologies.net/SAT/weather.txt'
response = requests.get(get_url)

# Create a filename with the current date
filename = 'Latest_TLE.txt'

# Create the full path for the file
full_path = os.path.join(path, filename)

# Save the downloaded content to the file
with open(full_path, 'wb') as file:
    file.write(response.content)

# Perform a POST request to upload the file
post_url = 'http://192.168.4.1/upload'
files = {'tlefile': (filename, open(full_path, 'rb'), 'text/plain')}
try:
    post_response = requests.post(post_url, files=files)
    post_response.raise_for_status() # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    
    print(f'Status Code: {post_response.status_code}')
    print(f'Response Content: {post_response.text}')
except requests.RequestException as e:
    print(f'An error occurred: {e}')