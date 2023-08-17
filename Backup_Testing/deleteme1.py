import time
import datetime
import csv



with open('/home/noaa_gms/RFSS/Tools/Report_Exports/schedule_short.csv', 'r') as csvfile:
    # Create a CSV reader object
    csvreader = csv.reader(csvfile)
    next(csvreader)

    current_weekday = datetime.datetime.utcnow().weekday()

    # lines = list.split('\n')
    for row in csvreader:
        #Splits the csv and removes parens, etc.
        # print(f'AOS: {aos_time}, LOS: {los_time}, SAT: {satellite_name}')
        # AOS: [14, 42, 17], LOS: [14, 57, 21], SAT: NOAA-15
        # AOS: [15, 9, 39], LOS: [15, 24, 4], SAT: NOAA-19
        aos_time = list(map(int, row[2][1:-1].split(',')))
        los_time = list(map(int, row[3][1:-1].split(',')))
        schedule_weekday = int(row[1])
        now = datetime.datetime.utcnow()
        satellite_name = row[4]

        # Format aos_datetime and los_datetime for use
        # print(f'AOS: {aos_datetime}, LOS: {los_datetime}')
        # AOS: 2023-08-14 14:42:17, LOS: 2023-08-14 14:57:21
        # AOS: 2023-08-14 15:09:39, LOS: 2023-08-14 15:24:04
        aos_datetime = datetime.datetime(now.year, now.month, now.day, *aos_time)
        los_datetime = datetime.datetime(now.year, now.month, now.day, *los_time)
        
        # If current time has already passed the scheduled los_datetime, skip to the next schedule
        if now > los_datetime or current_weekday != schedule_weekday:
            print(f'>>> Now: {now} - LOS: {los_datetime}')
            continue

        if now < aos_datetime and current_weekday == schedule_weekday:
            print(f'<<< Now: {now} - LOS: {aos_datetime}')
            time.sleep(1)  # Sleep for 5 seconds to not hog the CPU
            print('Waiting for next schedule')
            now = datetime.datetime.utcnow()