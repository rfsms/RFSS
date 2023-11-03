#!/usr/bin/env python3
from RsInstrument import RsInstrument, RsInstrException
import csv
import time
import datetime
import os 
import logging
from pymongo import MongoClient
import shutil
import re

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
REMOTE_IP = 'noaa-gms-ec2'
REMOTE_USERNAME = 'Administrator'
REMOTE_PATH = '/'
RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0'
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
INSTR = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
# INSTR = RsInstrument(RESOURCE_STRING, False, False, 'simulate=True')
INSTR_DIR = 'c:\\R_S\\Instr\\user\\RFSS\\'
DEMOD_DIR = '/home/noaa_gms/RFSS/toDemod/'

def move_iq_files_toDemod(temp_dir, to_demod_path):
    # logging.info('Running move_iq_files_toDemod()')
    try:
        iq_files = [file for file in os.listdir(temp_dir) if file.endswith('.iq.tar') or file == 'Simulating'] #Simulating in case of simulate=true
    except FileNotFoundError:
        return False

    if not iq_files:
        logging.info('No IQ files found')
        return False
    
    if 'Simulating' in iq_files:
        dest_folder_name = 'Simulating'
    else:
        try:
            earliest_file = min(iq_files)
            dest_folder_name = re.search(r'(\d{4}-\d{2}-\d{2})', earliest_file).group(1).replace('-', '_')
        except AttributeError:
            return False

    dest_folder = os.path.join(to_demod_path, dest_folder_name)
    
    try:
        os.makedirs(dest_folder, exist_ok=True)
        os.makedirs(os.path.join(dest_folder, 'results'), exist_ok=True)
    except PermissionError:
        return False

    for file in iq_files:
        try:
            shutil.move(os.path.join(temp_dir, file), os.path.join(dest_folder, file))
        except (FileNotFoundError, PermissionError):
            return False

    return True

# Function to get contents of c:\R_S\Instr\user\RFSS\ on Spectrum Analyzer download locally to /home/noaa_gms/RFSS/Received 
# These files will be called something like "2023-08-02_19_00_07_UTC_NOAA-15.iq.tar"
def get_SpecAn_content_and_DL_locally(INSTR):
    try:
        # Set and list the current directory on the SA
        INSTR.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = INSTR.query('MMEM:CAT?')

        # Process the response and log the content
        content_list = response.replace('\'', '').split(',')
        logging.info("Transferring captures from Spectrum Analyzer to process on RFSS server.")
        for item in content_list:
            # logging.info(item)

            # Download each file in the directory (skip directories)
            if not item.endswith('/'):  # Skip directories
                temp_filename = TEMP_DIR + item  # Set the destination path on your PC
                instrument_filename = INSTR_DIR + item  # Set the SA file path

                try:
                    # Download the file
                    data = INSTR.read_file_from_instrument_to_pc(instrument_filename, temp_filename)

                    # Check if data is not None before writing to the file
                    if data is not None:
                        with open(temp_filename, 'wb') as f:
                            f.write(data)

                    else:
                        continue

                except Exception as e:
                    logging.info(f"Error while downloading file '{item}': {str(e)}")

        logging.info('Removing files from Spectrum Analyzer')    
        INSTR.write(f'MMEM:DEL "{INSTR_DIR}*"')
    
    except RsInstrException as e:
        if "-256," in str(e):
            logging.info("No files on Spectrum Analyzer to process:", e)

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
        if restart_message:
            logging.info(restart_message)
        if loop_completed is not None:
            loop_completed[0] = False  # Use list to make it mutable

    return was_paused

# This function is the timing behind RFSS data capture.  Reads the CSV_FILE_PATH and goes through each row determining
# aos/los, etc and compares against current time.  If older entries exist continue, if current time meet aos time then 
# wait.  once current time matches an aos data is being captured until los.
# Finally, get_SpecAn_content_and_DL_locally(INSTR) & local_tgz_and_rm_IQ(TEMP_DIR, satellite_name) are processed
def process_schedule():
    logging.info("Successfully started process_schedule().  Waiting for next pass...")
    """Process the CSV schedule."""
    # Initializing pause flag at various states
    loop_completed = [True] 

    with open(CSV_FILE_PATH, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)

        # Go through rows
        for row in csvreader:
            # logging.info(row)
            # Check for pause flag at the start of each row
            handle_pause("Pause flag detected at start of row.", "Pause_flag removed. Restarting schedule...", loop_completed=loop_completed)

            if len(row) < 5:
                # logging.info(f"Skipping row {row} - not enough elements")
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
            
            # # Check if LOS time is on the next day - need to address this correctly
            # if los_datetime < aos_datetime:
            #     los_datetime += datetime.timedelta(days=1)

            # If current time has already passed the scheduled los_datetime, skip to the next schedule
            if now > los_datetime:
                continue

            # If current time is before the scheduled aos_datetime, wait until aos_datetime is reached
            while now < aos_datetime:
                handle_pause("Pause flag detected. Pausing pass schedule.", "Pause_flag removed. Restarting schedule...", sleep_time=1, loop_completed=loop_completed)
                now = datetime.datetime.utcnow()
                time.sleep(1)

            # Adding a trigger to provide single hit logging and start running
            triggered = False

            #Between AOL/LOS time
            while True:
                handle_pause("Schedule paused. Waiting for flag to be removed.", "Pause_flag removed. Restarting schedule...", loop_completed=loop_completed)

                now = datetime.datetime.utcnow()
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

                # Instrumentation happens here
                INSTR.write('INST IQ')
                INSTR.write('INIT:IMM;*WAI')
                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                time_saved_IQ = f"'{INSTR_DIR}{formatted_current_datetime}_{satellite_name}'"
                INSTR.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
                time.sleep(2) 
            
            get_SpecAn_content_and_DL_locally(INSTR)
            # success = local_tgz_and_rm_IQ(TEMP_DIR, satellite_name)
            success = move_iq_files_toDemod(TEMP_DIR, DEMOD_DIR)
            
            # Only execute this part if the loop was not broken by the pause flag
            if loop_completed:
                document_update = {
                    "$set": {
                        "processed": str(success)  # Assuming success is either "true" or "false"
                    }
                }
                schedule_run.update_one({"timestamp": document["timestamp"]}, document_update)

def main():
    logging.info("Starting RFSS_FSV main routine")

    # Instrument reset/setup
    idn = INSTR.query('*IDN?')
    instrument = idn.replace("Hello, I am: ", "")
    logging.info(f"Setting Up '{instrument}' at {RESOURCE_STRING}")
    
    INSTR.reset()
    INSTR.clear_status()
    INSTR.visa_timeout = 20000
    INSTR.write('SYST:DISP:UPD ON')
    INSTR.write('INIT:CONT ON')
    INSTR.write('SENS:FREQ:CENT 1702500000')
    INSTR.write('SENS:FREQ:SPAN 8000000')
    INSTR.write('SENS:BAND:RES 5000')
    INSTR.write('SENS:BAND:VID:AUTO OFF')
    INSTR.write('SENS:BAND:VID 5000')
    INSTR.write('INP:ATT:AUTO OFF')
    INSTR.write('INP:ATT 0')
    INSTR.write('DISP:WIND:SUBW:TRAC:Y:SCAL:RLEV -30')
    INSTR.write('DISP:WIND1:SUBW:TRAC1:MODE AVER')
    INSTR.write('SENS:WIND1:DET1:FUNC RMS')
    INSTR.write('DISP:WIND1:SUBW:TRAC2:MODE MAXH')
    INSTR.write('SENS:WIND1:DET2:FUNC RMS')
    INSTR.write('DISP:WIND1:SUBW:TRAC1:Y:SCAL 100') 
    INSTR.write('DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110')
    INSTR.write('CALC1:SGR:STAT ON')
    INSTR.write('CALC2:SGR:COL RAD')
    INSTR.write("INST:CRE:NEW IQ, 'IQ Analyzer'")
    INSTR.write('INIT:CONT OFF')
    INSTR.write('TRAC:IQ:SRAT 6250000') # For 5MHz channel, 10MHz==15.36MHz, 15MHz==18.75MHz
    INSTR.write('SENS:SWE:TIME 0.016')
    INSTR.write('SENS:SWE:COUN 10')
    INSTR.write('HCOP:DEV:LANG PNG')

    try:
        process_schedule()
        logging.info("Schedule finished for the day.\n")
        # logging.info("Successfully executed process_schedule() of the main routine")
    except Exception as e:
        logging.info(f"An error occurred: {e}")

if __name__ == "__main__":
    main()