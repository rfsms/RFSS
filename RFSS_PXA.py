#!/usr/bin/env python3
import pyvisa
import csv
import time
import datetime
import os 
import logging
from pymongo import MongoClient
from scipy.io import savemat

# Connection for MongoDB
client = MongoClient('localhost', 27017)
db = client['status_db']
schedule_run = db['schedule_run']
 
# Reset the Root Logger - this section is used to reset the root logger and then apply below configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# For production
csv_file_path = '/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv'
temp_dir = '/home/noaa_gms/RFSS/Received/'
resource_string= 'TCPIP::192.168.3.101::hislip0' 
rm = pyvisa.ResourceManager()
instr = rm.open_resource(resource_string, timeout = 5000)
demod_dir = '/home/noaa_gms/RFSS/toDemod/'
trigger = -56

def opc_check():
    """ Check if all preceding commands are completed """
    instr.write('*OPC')
    opc_value = instr.query('*OPC?').strip()
    # print(f"Initial *OPC? response: {opc_value}")

    # If *OPC? is not 1, enter a loop and wait for it to become 1
    while opc_value != '1':
        time.sleep(0.1)
        opc_value = instr.query('*OPC?').strip()
        print(f"Current *OPC? response: {opc_value}")

def handle_pause(log_message, restart_message=None, sleep_time=5, loop_completed=None):
    log_flag = True
    was_paused = False
    while os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
        if log_flag:
            logging.info(log_message)
            log_flag = False
        was_paused = True
        time.sleep(sleep_time)
    
    if was_paused:
        #Re-setup SpecAn
        instr.write("INST:SCR:SEL 'IQ Analyzer 1'")
        opc_check()

        if restart_message:
            logging.info(restart_message)
        if loop_completed is not None:
            loop_completed[0] = False  # Use list to make it mutable

    return was_paused

def process_schedule():
    """
    This function is the timing behind RFSS data capture.  Reads the CSV_FILE_PATH and goes through each row determining
    aos/los, etc and compares against current time.  If older entries exist continue, if current time meet aos time then 
    wait.  Once current time matches an aos, data is being captured until los.
    FOR MXA, between aos/los capture induvidual IQs send to Received from SA.  Finally after los, move Received/*.mat to toDemod for processing.
    """
    # Process the CSV schedule.
    loop_completed = [True]

    with open(csv_file_path, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)

        # Go through rows
        for row in csvreader:
            # Check for pause flag at the start of each row
            handle_pause("Pause flag detected at start of row.", "Pause_flag removed. Restarting schedule...", loop_completed=loop_completed)

            if len(row) < 5:
                logging.info(f"End of rows in schedule")
                continue

            aos_time = row[2][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            los_time = row[3][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)

            if len(aos_time) != 3 or len(los_time) != 3:
                logging.info(f"Skipping row {row} - invalid time format")
                continue

            satellite_name = row[4]
            now = datetime.datetime.utcnow()

            # Create aos_datetime and los_datetime for today
            aos_datetime = datetime.datetime(now.year, now.month, now.day, 
                                             int(aos_time[0]), int(aos_time[1]), int(aos_time[2]))
            los_datetime = datetime.datetime(now.year, now.month, now.day, 
                                             int(los_time[0]), int(los_time[1]), int(los_time[2]))

            # If current time has already passed the scheduled los_datetime, skip to the next schedule
            if now > los_datetime:
                continue

            # If current time is before the scheduled aos_datetime, wait until aos_datetime is reached
            while now < aos_datetime:
                handle_pause("Pause flag detected. Pausing pass schedule.", "Pause_flag removed. Restarting schedule...", sleep_time=1, loop_completed=loop_completed)
                now = datetime.datetime.utcnow()
                time.sleep(1)

            # Adding a trigger to provide single hit log and start running
            triggered = False

            #Between AOL/LOS time
            while True:
                handle_pause("Schedule paused. Waiting for flag to be removed.", "Pause_flag removed. Restarting schedule...", loop_completed=loop_completed)

                now = datetime.datetime.utcnow()  # Update current time at the start of each iteration
                if now >= los_datetime:
                    break

                if not triggered:
                    logging.info(f'Current scheduled row under test: {row}')
                    triggered = True

                    # Insert the data into MongoDB as a single document
                    document = {
                        "timestamp": datetime.datetime.utcnow(),
                        "row": row,
                        }
                    schedule_run.insert_one(document)

                operation_status_str = instr.query(':STATus:OPERation:CONDition?').strip()
                operation_status_dec = int(operation_status_str)
                
                # Interpret the operation status and print the corresponding state
                if operation_status_dec == 24:
                    print(f"Operation Status Register (DEC): {operation_status_dec} -- Triggered, Fetching Data")
                    
                    # Fetch and process data
                    data = instr.query_binary_values(":FETCH:WAV0?")

                    # Convert to separate I and Q arrays
                    i_data = data[::2]
                    q_data = data[1::2]

                    current_datetime = datetime.datetime.utcnow()

                    # Determine daily folders and file path
                    daily_folder_name = current_datetime.strftime('%Y_%m_%d')
                    daily_folder = os.path.join(demod_dir, daily_folder_name)
                    os.makedirs(daily_folder, exist_ok=True)

                    # Determine Quarter of the Day for quarterly folder saves
                    hour = current_datetime.hour
                    if hour < 6:
                        quarter_folder_name = '0000-0559'
                    elif hour < 12:
                        quarter_folder_name = '0600-1159'
                    elif hour < 18:
                        quarter_folder_name = '1200-1759'
                    else:
                        quarter_folder_name = '1800-2359'

                    # Quarter Folder saves
                    quarter_folder = os.path.join(daily_folder, quarter_folder_name)
                    os.makedirs(quarter_folder, exist_ok=True)

                    results_folder = os.path.join(daily_folder, 'results')
                    os.makedirs(results_folder, exist_ok=True)

                    # Save I/Q data to MAT file in the Quarter Folder
                    formatted_current_datetime = current_datetime.strftime('%Y%m%d_%H%M%S_UTC') 
                    mat_file_path = os.path.join(quarter_folder, f'{formatted_current_datetime}_{satellite_name}.mat')
                    savemat(mat_file_path, {'I_Data': i_data, 'Q_Data': q_data})
            
            # Only execute this part if the loop was not broken by the pause flag
            if loop_completed[0]:  # Check if loop completed successfully
                document_update = {
                    "$set": {
                        "processed": "true"  # Set processed to "true" as the loop completed successfully
                    }
                }
                schedule_run.update_one({"timestamp": document["timestamp"]}, document_update)
                logging.info("Scheduled row completed successfully!")
            else:
                document_update = {
                    "$set": {
                        "processed": "false"  # Set processed to "false" as the loop did not complete successfully
                    }
                }
                schedule_run.update_one({"timestamp": document["timestamp"]}, document_update)
                logging.info("Scheduled row encountered errors.")

def main():
    logging.info("Starting RFSS_PXA main routine")

    # Instrument reset/setup
    idn = instr.query("ID?")
    # instrument = idn.replace("Hello, I am: ", "")
    logging.info(f"Setting Up {idn.split()} at {resource_string}")
    
    #Reset SpecAn
    instr.write("*RST")
    instr.write("*CLS")
    instr.write("SYST:DEF SCR")

    # Setup Spectrum Analyzer
    instr.write("INST:NSEL 1")
    instr.write("INIT:CONT OFF")
    instr.write("SENS:FREQ:SPAN 20000000")
    instr.write("SENS:FREQ:CENT 1702500000")
    instr.write("POW:ATT:AUTO ON")
    # instr.write("POW:ATT 0")
    instr.write("POW:GAIN ON")
    instr.write("BAND 5000")
    instr.write("DISP:WIND:TRAC:Y:RLEV -20dBm")
    instr.write("TRAC1:TYPE WRIT")
    instr.write("DET:TRAC1 NORM")
    instr.write("TRAC2:TYPE MAXH")
    instr.write("DET:TRAC2 POS")
    instr.write("AVER:COUNT 10")
    opc_check()
    # print("SA Setup Complete")

    #Create IQ window
    instr.write("INST:SCR:CRE")
    instr.write("INST:NSEL 8")
    instr.write("INIT:CONT ON")
    opc_check()
    # print("IQ Window Setup Complete")

    #Conf IQ 
    instr.write("CONF:WAV")
    instr.write("SENS:FREQ:CENT 1702500000")
    instr.write("POW:GAIN ON")
    instr.write("WAV:SRAT 18.75MHz")
    instr.write("WAV:SWE:TIME 160ms")
    instr.write("DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON")
    instr.write("FORM:BORD SWAP")
    instr.write("FORM REAL,32")    
    opc_check()
    # print("IQ Setup Complete")

    #Conf Video Trigger
    instr.write("TRIG:WAV:SOUR VID")
    instr.write(f"TRIG:VID:LEV {trigger}")
    opc_check()
    # print("Video Setup Complete")

    try:
        process_schedule()
        instr.write("DISP:ENAB ON")
        logging.info("Schedule finished for the day.\n")
        instr.close()
    except Exception as e:
        logging.info(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
