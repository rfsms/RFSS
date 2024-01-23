#!/usr/bin/env python3
from http.client import http
import json
import pyvisa
import csv
import time
import datetime
import os 
import logging
from pymongo import MongoClient
from scipy.io import savemat
import subprocess

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
CSV_FILE_PATH = '/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv'
TEMP_DIR = '/home/noaa_gms/RFSS/Received/'
RESOURCE_STRING = 'TCPIP::192.168.3.101::hislip0' 
RM = pyvisa.ResourceManager()
INSTR = RM.open_resource(RESOURCE_STRING, timeout = 20000)
DEMOD_DIR = '/home/noaa_gms/RFSS/toDemod/'

def restart_service(service_name):
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', service_name], check=True)
        logging.info(f"Successfully restarted the service {service_name}.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart the service {service_name}: {e}")

def opc_check(INSTR):
    """ Check if all preceding commands are completed """
    INSTR.write('*OPC')
    opc_value = INSTR.query('*OPC?').strip()
    # logging.info(f"OPC Check: {opc_value}")

    # If *OPC? is not 1, enter a loop and wait for it to become 1
    if opc_value != '1':
        while True:
            time.sleep(0.5)
            opc_value = INSTR.query('*OPC?').strip()
            print(f"Current *OPC? response: {opc_value}")
            if opc_value == '1':
                break

def get_current_AzEl():
    conn = http.client.HTTPConnection("192.168.4.1", 80)
    conn.request("GET", "/min")
    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    return round(data['az']), round(data['el'])

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
        #Resetup SpecAn
        INSTR.write("INST:SCR:SEL 'IQ Analyzer 1'")
        opc_check(INSTR)
        logging("Instrument after pause successful")

        if restart_message:
            logging.info(restart_message)
        if loop_completed is not None:
            loop_completed[0] = False

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

    with open(CSV_FILE_PATH, 'r') as csvfile:
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

                # Get current Azimuth and Elevation
                azimuth, elevation = get_current_AzEl()

                # Intrumentation happens here
                INSTR.write('INIT:IMM;*WAI')
                # INSTR.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
                data = INSTR.query_binary_values(":FETCH:WAV0?")
                opc_check(INSTR)

                # Convert to separate I and Q arrays
                i_data = data[::2]
                q_data = data[1::2]

                current_datetime = datetime.datetime.utcnow()

                # Daily Folders
                daily_folder_name = current_datetime.strftime('%Y_%m_%d')
                daily_folder = os.path.join(DEMOD_DIR, daily_folder_name)
                os.makedirs(daily_folder, exist_ok=True)

                # Determine Quarter of the Day
                hour = current_datetime.hour
                if hour < 6:
                    quarter_folder_name = '0000-0559'
                elif hour < 12:
                    quarter_folder_name = '0600-1159'
                elif hour < 18:
                    quarter_folder_name = '1200-1759'
                else:
                    quarter_folder_name = '1800-2359'

                # Quarter Folder
                quarter_folder = os.path.join(daily_folder, quarter_folder_name)
                os.makedirs(quarter_folder, exist_ok=True)

                # Create results folder in each quarterly folder - instead of daily folder
                results_folder = os.path.join(quarter_folder, 'results')
                os.makedirs(results_folder, exist_ok=True)

                # Save I/Q data to MAT file in the Quarter Folder
                formatted_current_datetime = current_datetime.strftime('%Y%m%d_%H%M%S_UTC') 
                mat_file_path = os.path.join(quarter_folder, f'{formatted_current_datetime}_{satellite_name}_AZ_{azimuth}_EL_{elevation}.mat')
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
    idn = INSTR.query("ID?")
    # instrument = idn.replace("Hello, I am: ", "")
    logging.info(f"Setting Up {idn.split()} at {RESOURCE_STRING}")
    
    #Reset SpecAn
    INSTR.write("*RST")
    INSTR.write("*CLS")
    INSTR.write("SYST:DEF SCR")
    opc_check(INSTR)
    logging.info("Reset Succesful")

    # Setup Spectrum Analyzer
    INSTR.write("INST:NSEL 1")
    INSTR.write("INIT:CONT OFF")
    INSTR.write("SENS:FREQ:SPAN 20000000")
    INSTR.write("SENS:FREQ:CENT 1702500000")
    INSTR.write("POW:ATT:AUTO ON")
    # INSTR.write("POW:ATT 0")
    INSTR.write("POW:GAIN ON")
    INSTR.write("BAND 5000")
    INSTR.write("DISP:WIND:TRAC:Y:RLEV -20dBm")
    INSTR.write("TRAC1:TYPE WRIT")
    INSTR.write("DET:TRAC1 NORM")
    INSTR.write("TRAC2:TYPE MAXH")
    INSTR.write("DET:TRAC2 POS")
    INSTR.write("AVER:COUNT 10")
    opc_check(INSTR)
    logging.info("SA Setup Succesful")

    #Create IQ window
    INSTR.write("INST:SCR:CRE")
    INSTR.write("INST:NSEL 8")
    INSTR.write("CONF:WAV")
    INSTR.write("SENS:FREQ:CENT 1702500000")
    # INSTR.write("DISP:WAV:VIEW:NSEL 1")
    INSTR.write("POW:GAIN ON")
    INSTR.write("WAV:SRAT 18.75MHz")
    INSTR.write("WAV:SWE:TIME 160ms")
    INSTR.write("DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON")
    INSTR.write("FORM:BORD SWAP")
    INSTR.write("FORM REAL,32")
    opc_check(INSTR)
    logging.info("IQ Setup Succesful")

    try:
        process_schedule()
        INSTR.write("DISP:ENAB ON")
        logging.info("Schedule finished for the day.\n")
    except Exception as e:
        logging.info(f"An error occurred in RFSS_PXA.py: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred in RFSS_PXA.py: {e}")
        if "Connection timed out" in str(e):
            restart_service('RFSS.service')