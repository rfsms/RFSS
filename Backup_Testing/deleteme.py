import datetime
import time
import csv

CSV_FILE_PATH = '/home/noaa_gms/RFSS/Backup_Testing/schedule.csv'
with open(CSV_FILE_PATH, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        
        # Skip header
        next(csvreader)

        # Go through rows
        for row in csvreader:
            now = datetime.datetime.utcnow()
            aos_time = row[2][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            los_time = row[3][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            
            now = datetime.datetime.utcnow()
            satellite_name = row[4]

            # Create aos_datetime and los_datetime for today
            aos_datetime = datetime.datetime(now.year, now.month, now.day, 
                                             int(aos_time[0]), int(aos_time[1]), int(aos_time[2]))
            los_datetime = datetime.datetime(now.year, now.month, now.day, 
                                             int(los_time[0]), int(los_time[1]), int(los_time[2]))


            # If current time has already passed the scheduled los_datetime, skip to the next schedule
            if now > los_datetime:
                print('now is > than los_datetime')
                continue
                
            # If current time is before the scheduled aos_datetime, wait until aos_datetime is reached
            while now < aos_datetime:
                time.sleep(1)  # Sleep for 5 seconds to not hog the CPU
                print('Waiting for next schedule')
                now = datetime.datetime.utcnow()

            while True:
                now = datetime.datetime.utcnow()  # Update current time at the start of each iteration
                if now >= los_datetime:
                    break

                # intrumentation happens here
                #print(f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Function with label '{satellite_name}' is running!")
                print('Instr function running')
                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                # time_saved_IQ = f"'{INSTR_DIR}{formatted_current_datetime}_{satellite_name}'"
                # print(f'To Be saved: {time_saved_IQ}')
                print('Instr saving')
                # print('Waiting for 10 IQ sweeps...')
                time.sleep(1)  # Sleep for 1 second
            
            # print_message(satellite_name)
            # get_SpecAn_content_and_DL_locally(INSTR)
            # local_tgz_and_rm_IQ(TEMP_DIR, satellite_name)