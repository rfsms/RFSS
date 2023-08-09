import csv
import time
import datetime

file_path = "/home/noaa_gms/RFSS/Backup_Testing/schedule.csv"

# # now availble globally for all functions
# now = datetime.datetime.utcnow()

def print_message(satellite_name):
    """Simple function to print a message."""
    now = datetime.datetime.utcnow()
    print(f'Message processed for {satellite_name} at LOS of {now.strftime("%Y-%m-%d %H:%M:%S")}!')

def process_schedule():
    """Process the schedule CSV."""
    with open(file_path, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        
        # Skip header
        next(csvreader)

        # Go through rows
        for row in csvreader:
            aos_time = row[1][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            los_time = row[2][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            
            now = datetime.datetime.utcnow()
            satellite_name = row[3]

            # Create los_datetime for today
            los_datetime = datetime.datetime(now.year, now.month, now.day, 
                                             int(los_time[0]), int(los_time[1]), int(los_time[2]))

            # If current time has already passed the scheduled los_datetime, skip to the next schedule
            if now > los_datetime:
                continue
                
            while True:
                now = datetime.datetime.utcnow()  # Update current time at the start of each iteration
                if now >= los_datetime:
                    break
                # intrumentation happens here
                # print(f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(5)  # Sleep for 1 second
            
            print_message(satellite_name)


def main():
    try:
        # Create schedule for debug
        num_of_entries = 5

        now = datetime.datetime.utcnow()
        start_times = [(now + datetime.timedelta(seconds=10 + i*23)).time() for i in range(num_of_entries)]
        end_times = [(now + datetime.timedelta(seconds=20 + i*23)).time() for i in range(num_of_entries)]

        with open("/home/noaa_gms/RFSS/Backup_Testing/schedule.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Day of Week", "AOS", "LOS", "Satellite"])
            for i in range(num_of_entries):
                writer.writerow([now.weekday() + 1, str((start_times[i].hour, start_times[i].minute, start_times[i].second)), 
                                str((end_times[i].hour, end_times[i].minute, end_times[i].second)), f"NOAA-{15 + i}"])
        # End schdule for debug 

        process_schedule()
        print("Script finished.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
