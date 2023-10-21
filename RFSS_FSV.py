#!/usr/bin/env python3
from RsInstrument import RsInstrument, RsInstrException
import csv
import time
import datetime
import os 
import tarfile
import glob
import subprocess
import logging
from pymongo import MongoClient

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
        logging.info('All files in the source directory have been removed.')
        logging.info('----------------------------------------------------')
    else:
        logging.info('Error while moving files.')

# Function to tar.gz all files in /home/noaa_gms/RFSS/Received/* with a satName_timestamp and then delete all *.iq.tar.  Then scp all files to E2 using the scp function
# These files will be called someting like "NOAA15_2023-08-02_19_00_00_UTC.tar.gz" and will be comprised of the above *.iq.tar files
# After calling, this function calls mv_tar_files_to_preUpload for rsync
def local_tgz_and_rm_IQ(directory, satellite):
    current_datetime = datetime.datetime.utcnow()
    formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC')
    
    # Get a list of all files in the directory
    all_files = [os.path.join(directory, file) for file in os.listdir(directory)]

    # Create the name of the final tar.gz file
    gz_file = os.path.join(directory, f'{formatted_current_datetime}_{satellite}.tar.gz')

    # Create the tar.gz archive
    with tarfile.open(gz_file, 'w:gz') as tar:
        for file in all_files:
            tar.add(file, arcname=os.path.basename(file))
    
    # Remove the original files
    for file in all_files:
        os.remove(file)

    # Check if the gz_file exists before proceeding
    if os.path.exists(gz_file):
        logging.info('Rsyncing *.tar.gz files and removing locally')
        mv_tar_files_to_preUpload(TEMP_DIR)
        return "true"
    else:
        logging.info(f"No '{gz_file}' found. Skipping scp_gz_files_and_delete.")
        return "false"

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

# This function is the timing behind RFSS data capture.  Reads the CSV_FILE_PATH and goes through each row determining
# aos/los, etc and compares against current time.  If older entries exist continue, if current time meet aos time then 
# wait.  once current time matches an aos data is being captured until los.
# Finally, get_SpecAn_content_and_DL_locally(INSTR) & local_tgz_and_rm_IQ(TEMP_DIR, satellite_name) are processed
def process_schedule():
    """Process the CSV schedule."""
    # Initializing pause flag at various states
    loop_completed = True
    log_pause_msg_start_of_row = True 

    with open(CSV_FILE_PATH, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)

        # Go through rows
        for row in csvreader:
            # Check for pause flag at the start of each row
            while os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                if log_pause_msg_start_of_row:
                    logging.info("Pause flag detected at start of row. Pausing.")
                    log_pause_msg_start_of_row = False  # Set to False so the message is not logged again
                time.sleep(5)  # Sleep for 5 seconds before checking again

            # Reset the logging flag if pause_flag.txt is removed
            if not os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                log_pause_msg_start_of_row = True

            # Reset the flag here to reset for each row
            loop_completed = True

            if len(row) < 5:
                logging.info(f"Skipping row {row} - not enough elements")
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

            was_paused = False  # Initialize the flag here
            log_pause_msg = True  # Initialize another flag to control the logging message

            # If current time is before the scheduled aos_datetime, wait until aos_datetime is reached
            while now < aos_datetime:
                if os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                    if log_pause_msg:
                        logging.info("Pause flag detected. Pausing pass schedule.")
                        log_pause_msg = False  # Set to False so the message is not logged again
                    was_paused = True  # Set the flag because the schedule was paused
                    loop_completed = False
                    time.sleep(1)
                else:
                    log_pause_msg = True  # Reset the logging flag if pause_flag.txt is removed
                    if was_paused:
                        logging.info("Pause_flag removed. Restarting schedule...")
                        was_paused = False  # Reset the flag
                now = datetime.datetime.utcnow()

            # Adding a trigger to provide single hit logging and start running
            triggered = False
            while True:
                was_paused = False  # Pause flag initialization 

                now = datetime.datetime.utcnow()
                if now >= los_datetime:
                    break

                if os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                    if now < aos_datetime or now > los_datetime:
                        loop_completed = False  # Setting this to False as it's breaking because of pause_flag.txt
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
                
                log_pause_msg_inside_loop = True  # Initialize another flag to control the logging message

                while os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                    if log_pause_msg_inside_loop:
                        logging.info("Schedule paused. Waiting for flag to be removed.")
                        log_pause_msg_inside_loop = False  # Set to False so the message is not logged again
                    was_paused = True  # Set the flag because the schedule is paused
                    time.sleep(5)

                # Reset the logging flag if pause_flag.txt is removed
                if not os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                    log_pause_msg_inside_loop = True

                # If the schedule is unpaused and schedule restarted during a pass
                if was_paused:
                    logging.info(f"Restarting schedule during pass. Current scheduled row under test: {row}")
                    was_paused = False  # Reset the flag

                if os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                    loop_completed = False
                    break

                # Instrumentation happens here
                INSTR.write('INST IQ')
                INSTR.write('INIT:IMM;*WAI')
                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                time_saved_IQ = f"'{INSTR_DIR}{formatted_current_datetime}_{satellite_name}'"
                INSTR.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
                time.sleep(2) 
            
            get_SpecAn_content_and_DL_locally(INSTR)
            success = local_tgz_and_rm_IQ(TEMP_DIR, satellite_name)
            
            # Only execute this part if the loop was not broken by the pause flag
            if loop_completed:
                document_update = {
                    "$set": {
                        "processed": success  # Assuming success is either "true" or "false"
                    }
                }
                schedule_run.update_one({"timestamp": document["timestamp"]}, document_update)


def main():

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
    INSTR.write('TRAC:IQ:SRAT 6250000') # For 5MHz channel
    INSTR.write('SENS:SWE:TIME 0.016')
    INSTR.write('SENS:SWE:COUN 10')
    INSTR.write('HCOP:DEV:LANG PNG')

    try:
        process_schedule()
        logging.info("Schedule finished for the day.\n")
    except Exception as e:
        logging.info(f"An error occurred: {e}")

if __name__ == "__main__":
    main()