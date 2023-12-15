#!/usr/bin/env python3
import pyvisa
import csv
import time
import datetime
import os 
import glob
import subprocess
import logging
from pymongo import MongoClient
from scipy.io import savemat
import sys

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
RESOURCE_STRING = 'TCPIP::192.168.3.101::hislip0' 
RM = pyvisa.ResourceManager()
INSTR = RM.open_resource(RESOURCE_STRING, timeout = 20000)
INSTR_DIR = 'D:\\Users\\Instrument\\Documents\\BASIC\\data\\WAV\\results\\RFSS\\'

# Once the files are removed fromSpecAn, tar/gz'd in TEMP_DIR folder, then this function moves the file into
# preUpload to get rsync'd when connectivity to EC2 is available.  
# Uploads is triggered by/usr/local/bin/rsyncUpload.sh service and happens whenever a new file is placed in the dir.
def mv_tar_files_to_preUpload(source_dir):
    file_list = glob.glob(os.path.join(source_dir, '*tar.gz'))
    if not file_list:
        logging.info('No *.tar.gz files found in the source directory.')
        return

    destination_path = "/home/noaa_gms/RFSS/preUpload/"
    process = subprocess.run(["mv", *file_list, destination_path])

    if process.returncode == 0:
        # Removing all files in the source directory
        subprocess.run(["rm", "-f", os.path.join(source_dir, '*')])
        logging.info('All tar.gz files in the "Received" directory have been moved to preUpload.')
        logging.info('----------------------------------------------------')
    else:
        logging.info('Error while moving files.')

# Function to tar.gz all files in /home/noaa_gms/RFSS/Received/* with a satName_timestamp and then delete all *.iq.tar.  Then scp all files to E2 using the scp function
# These files will be called someting like "NOAA15_2023-08-02_19_00_00_UTC.tar.gz" and will be comprised of the above *.iq.tar files
# After calling, this function calls mv_tar_files_to_preUpload for rsync
def local_tgz_and_rm_IQ(directory, satellite):
    current_datetime = datetime.datetime.utcnow()
    formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC')
    
    all_files = [file for file in os.listdir(directory)]
    gz_file = os.path.join(directory, f'{formatted_current_datetime}_{satellite}.tar.gz')
    
    process = subprocess.run(['tar', 'czf', gz_file, '-C', directory] + all_files)
    
    if process.returncode == 0:
        for file in all_files:
            os.remove(os.path.join(directory, file))
    else:
        logging.error(f'Error creating tar.gz file: {gz_file}')
        return False

    if os.path.exists(gz_file):
        logging.info('All files have been tar/compressed and will be moved to preUpload')
        mv_tar_files_to_preUpload(TEMP_DIR)
        return True
    else:
        logging.error(f"No '{gz_file}' found. Skipping scp_gz_files_and_delete.")
        return False

def handle_pause(INSTR, log_message, restart_message=None, sleep_time=5, loop_completed=None):
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
        # INSTR.write("INST:NSEL 8")
        INSTR.write("CONF:WAV")
        INSTR.write("INIT:CONT OFF")
        INSTR.write('SENS:FREQ:CENT 1702500000')
        INSTR.write('POW:ATT:AUTO OFF')
        INSTR.write('POW:ATT 0')
        INSTR.write('DISP:WAV:VIEW:NSEL 1')
        INSTR.write('POW:GAIN ON')
        INSTR.write('WAV:SRAT 18.75MHz')
        INSTR.write('WAV:SWE:TIME 16ms')
        INSTR.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
        INSTR.write("FORM:BORD SWAP")
        INSTR.write("FORM REAL,32")

        if restart_message:
            logging.info(restart_message)
        if loop_completed is not None:
            loop_completed[0] = False  # Use list to make it mutable

    return was_paused

# This function is the timing behind RFSS data capture.  Reads the CSV_FILE_PATH and goes through each row determining
# aos/los, etc and compares against current time.  If older entries exist continue, if current time meet aos time then 
# wait.  once current time matches an aos data is being captured until los.
# Finally, get_SpecAn_content_and_DL_locally(INSTR) & local_tgz_and_rm_IQ(TEMP_DIR, satellite_name) are processed
def process_schedule(INSTR):
    """Process the CSV schedule."""
    # Initializing pause flag
    loop_completed = [True]

    with open(CSV_FILE_PATH, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)

        # Go through rows
        for row in csvreader:
            # Check for pause flag at the start of each row
            handle_pause(INSTR, "Pause flag detected at start of row.", "Pause_flag removed. Restarting schedule...", loop_completed=loop_completed)

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
                handle_pause(INSTR, "Pause flag detected. Pausing pass schedule.", "Pause_flag removed. Restarting schedule...", sleep_time=1, loop_completed=loop_completed)
                now = datetime.datetime.utcnow()
                time.sleep(1)

            # Adding a trigger to provide single hit log and start running
            triggered = False

            #Between AOL/LOS time
            while True:
                handle_pause(INSTR, "Schedule paused. Waiting for flag to be removed.", "Pause_flag removed. Restarting schedule...", loop_completed=loop_completed)

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

                # Intrumentation happens here
                INSTR.write('INIT:IMM;*WAI')
                # INSTR.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
                data = INSTR.query_binary_values(":FETCH:WAV0?")

                # Convert to separate I and Q arrays
                i_data = data[::2]
                q_data = data[1::2]

                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 

                # Save I/Q data to MAT file
                savemat(f'{TEMP_DIR}{formatted_current_datetime}_{satellite_name}.mat', {'I_Data': i_data, 'Q_Data': q_data})
                time.sleep(5)  # Sleep for 5 second for PXA
            
            # get_SpecAn_content_and_DL_locally(INSTR) -> unnecesary for PXA    
            success = local_tgz_and_rm_IQ(TEMP_DIR, satellite_name)
            
            # Only execute this part if the loop was not broken by the pause flag
            if loop_completed:
                document_update = {
                    "$set": {
                        "processed": str(success)  # Assuming success is either "true" or "false"
                    }
                }
                schedule_run.update_one({"timestamp": document["timestamp"]}, document_update)

def main(ip_address):

    RESOURCE_STRING = f'TCPIP::{ip_address}::hislip0' 
    RM = pyvisa.ResourceManager()
    INSTR = RM.open_resource(RESOURCE_STRING, timeout = 20000)

    logging.info("Starting RFSS_PXA main routine")

    # Instrument reset/setup
    idn = INSTR.query("*IDN?")
    instrument = idn.replace("Hello, I am: ", "")
    logging.info(f"Setting Up '{instrument}' at {RESOURCE_STRING}")
    
    #Reset SpecAn
    INSTR.write("*RST")
    INSTR.write("*CLS")
    INSTR.write("SYST:DEF SCR")

    # Setup Spectrum Analyzer
    INSTR.write("INST:NSEL 1")
    INSTR.write("INIT:CONT OFF")
    INSTR.write("SENS:FREQ:SPAN 20000000")
    INSTR.write("SENS:FREQ:CENT 1702500000")
    INSTR.write("POW:ATT:AUTO OFF")
    INSTR.write("POW:ATT 0")
    INSTR.write("BAND 5000")
    INSTR.write("DISP:WIND:TRAC:Y:RLEV -40dBm")
    INSTR.write("TRAC1:TYPE WRIT")
    INSTR.write("DET:TRAC1 NORM")
    INSTR.write("TRAC2:TYPE MAXH")
    INSTR.write("DET:TRAC2 POS")
    INSTR.write("AVER:COUNT 10")
    #Create IQ window
    INSTR.write("INST:SCR:CRE")
    INSTR.write("INST:NSEL 8")
    INSTR.write("CONF:WAV")
    INSTR.write("SENS:FREQ:CENT 1702500000")
    # INSTR.write("DISP:WAV:VIEW:NSEL 1")
    INSTR.write("POW:GAIN ON")
    INSTR.write("WAV:SRAT 18.75MHz")
    INSTR.write("WAV:SWE:TIME 16ms")
    INSTR.write("DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON")
    INSTR.write("FORM:BORD SWAP")
    INSTR.write("FORM REAL,32")

    try:
        process_schedule(INSTR)
        INSTR.write("DISP:ENAB ON")
        logging.info("Schedule finished for the day.\n")
    except Exception as e:
        logging.info(f"An error occurred: {e}")

## Added commented if statement below in cases where RFSS_PXA will be run as standalone 
if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     raise ValueError("Please provide an IP address for your spectrum analyzer.")
    # ip_address = sys.argv[1]
    # main(ip_address)
    main()