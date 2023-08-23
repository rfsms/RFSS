#!/usr/bin/env python3
import schedule
import time
import http.client
import datetime
import csv
import RFSS_Autonomous
import logging
import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['status_db']
schedule_collection = db['schedule_daily']

# Reset the Root Logger - this section is used to reset the root logger and then apply below configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Change this to increase/decrease schedule based on minimum elevation
minElevation = 5.0

# Check if the current time is 00:00 UTC or later, and if so, call RFSS_Autonomous.main()
if datetime.datetime.utcnow().time() >= datetime.time(0, 0):
    logging.info('-----------------------------------------------------')
    logging.info('RFSS service restarted. Using current schedule.')
    RFSS_Autonomous.main()

def fetchReport():
    try:
        logging.info(f"Fetching report for use.")
        conn = http.client.HTTPConnection("192.168.4.1", 80)
        conn.request("GET", "/report?a=38771;43689;25338;28654;33591")
        response = conn.getresponse()

        if response.status == 200:
            data = json.loads(response.read().decode())["list"][:-1]

            # Get the current day of the week and initialize an empty list to put the response in
            today = datetime.datetime.utcnow().weekday()
            rows = []

            # Response received -> define the data
            for entry in data:
                satellite = entry[1].replace(" ", "-")
                aos_time = datetime.datetime.utcfromtimestamp(entry[2])
                los_time = datetime.datetime.utcfromtimestamp(entry[3])
                day_of_week = aos_time.weekday()
                max_elevation = entry[7]
                
                # Make sure to drop any items in the schedule that are not today and that are above minElevation
                # We do this since teh schedule will provide a couple of days.  Since we are doing this daily
                # we restrict the schedule to avoid duplicates 
                if day_of_week == today and max_elevation > minElevation:
                    formatted_aos = f"({aos_time.hour},{aos_time.minute},{aos_time.second})"
                    formatted_los = f"({los_time.hour},{los_time.minute},{los_time.second})"
                    rows.append((aos_time, day_of_week, formatted_aos, formatted_los, satellite, max_elevation))

            # Sort the schedule list
            rows.sort(key=lambda x: x[0])

            # Write the scehdule to csv to use in RFSS_Autonomous.main()
            output_path = "/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv"
            with open(output_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Pass", "DayofWeek", "AOS", "LOS", "Satellite", "MaxElevation"])
                for index, row in enumerate(rows, start=1):
                    writer.writerow([index, row[1], row[2], row[3], row[4], row[5]])

            # Additionally add the schedule with write timestamp to mongoDB for use later 
            file_path = "/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv"
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = [row for row in reader]

                # Convert AOS and LOS into proper tuples
                for row in rows:
                    row['AOS'] = tuple(map(int, row['AOS'][1:-1].split(',')))
                    row['LOS'] = tuple(map(int, row['LOS'][1:-1].split(',')))
                    row['MaxElevation'] = float(row['MaxElevation'])

                # Insert the data into MongoDB as a single document
                document = {
                    "timestamp": datetime.datetime.utcnow(),
                    "schedule": rows,
                    }
                schedule_collection.insert_one(document)

            logging.info('New schedule extracted, logged and ready for use.')
            RFSS_Autonomous.main()
        
    except Exception as e:
        logging.error(f'An error occuredL {e}')

schedule.every().day.at("00:00").do(fetchReport)

while True:
    schedule.run_pending()
    time.sleep(1)