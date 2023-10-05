#!/usr/bin/env python3
import pyvisa
import csv
import time
import datetime
import os 
import tarfile
import glob
import subprocess
import logging
from pymongo import MongoClient
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
RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0' 
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
        INSTR.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = INSTR.query('MMEM:CAT?')
        # print(response)

        # Corrected the parsing
        content_list = [re.split(',,', item)[0] for item in re.findall(r'"(.*?)"', response)]
        # print("Content list:", content_list)
        
        for item in content_list:
            temp_filename = TEMP_DIR + item
            instrument_filename = INSTR_DIR + item
            # logging.info(f"Downloading {item}")

            try:
                INSTR.write(f'MMEM:DATA? "{instrument_filename}"')
                # INSTR.write(f'MMEM:DATA? "{instrument_filename}";*WAI')
                data = INSTR.read_raw()
                if data:
                    with open(temp_filename, 'wb') as f:
                        f.write(data)
            except Exception as e:
                logging.info(f"Error while downloading file '{item}': {str(e)}")

            INSTR.write(f'MMEM:DEL "{item}"')

    except pyvisa.errors.VisaIOError as e:
        if "-256," in str(e):
            logging.info("No files on Spectrum Analyzer to process:", e)


# This function is the timing behind RFSS data capture.  Reads the CSV_FILE_PATH and goes through each row determining
# aos/los, etc and compares against current time.  If older entries exist continue, if current time meet aos time then 
# wait.  once current time matches an aos data is being captured until los.
# Finally, get_SpecAn_content_and_DL_locally(INSTR) & local_tgz_and_rm_IQ(TEMP_DIR, satellite_name) are processed
def process_schedule():
    """Process the CSV schedule."""
    with open(CSV_FILE_PATH, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)

        # Go through rows
        for row in csvreader:
            aos_time = row[2][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            los_time = row[3][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
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
                time.sleep(1)
                now = datetime.datetime.utcnow()

            # Adding a trigger to provide single hit log and start running
            triggered = False
            while True:
                now = datetime.datetime.utcnow()  # Update current time at the start of each iteration
                if now >= los_datetime:
                    break

                # Lets see if this works...
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
                # print(f"Function with label '{satellite_name}' is running!")
                INSTR.write('INIT:IMM;*WAI')
                INSTR.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                time_saved_IQ = f"'{INSTR_DIR}{formatted_current_datetime}_{satellite_name}'"
                INSTR.write(f'MMEM:STOR:RES "{time_saved_IQ}"')
                time.sleep(10)  # Sleep for 5 second
            
            # # print_message(satellite_name)
            get_SpecAn_content_and_DL_locally(INSTR)
            # local_tgz_and_rm_IQ(TEMP_DIR, satellite_name)        
            success = local_tgz_and_rm_IQ(TEMP_DIR, satellite_name)
            
            # Assuming local_tgz_and_rm_IQ function is successful, update the MongoDB document
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
    
        #Reset SpecAn
    INSTR.write('*RST')
    INSTR.write('*CLS')
    INSTR.write('SYST:DEF SCR')

    # Configure Swept SA
    INSTR.write('DISP:ENAB OFF')
    INSTR.write('INIT:CONT ON')
    INSTR.write('DISP:VIEW SPEC')
    INSTR.write('SENS:FREQ:SPAN 20000000')
    INSTR.write('SENS:FREQ:CENT 1702500000')
    INSTR.write('SENS:BAND:RES 10000')
    INSTR.write('SENS:BAND:VID:AUTO OFF')
    INSTR.write('SENS:BAND:VID 10000')
    INSTR.write('POW:ATT:AUTO OFF')
    INSTR.write('POW:ATT 0')    
    INSTR.write('POW:GAIN ON')
    INSTR.write('TRAC1:DISP ON')
    INSTR.write('TRAC1:TYPE WRIT')
    INSTR.write('DET:TRACE1 AVER')
    INSTR.write('AVER:COUN 1')
    INSTR.write('TRAC2:DISP ON')
    INSTR.write('TRAC2:TYPE MAXH')
    INSTR.write('DET:TRACE2 AVER')
    INSTR.write('DISP:WIND:TRAC:Y:RLEV -50')
    INSTR.write('DISP:VIEW:SPEC:HUE 10')
    INSTR.write('DISP:VIEW:SPEC:REF 75')
    INSTR.write('DISP:VIEW:SPEC:BOTT 0')

    # Setup IQ Analyzer
    INSTR.write('INST:SCR:CRE')
    INSTR.write('INST:SEL BASIC')
    INSTR.write('CONF:WAV')
    INSTR.write('SENS:FREQ:CENT 1702500000')
    INSTR.write('POW:ATT:AUTO OFF')
    INSTR.write('POW:ATT 0')    
    INSTR.write('POW:GAIN ON')
    INSTR.write('DISP:WAV:VIEW:NSEL 1')
    INSTR.write('POW:GAIN ON')
    INSTR.write('WAV:SRAT 18.75MHz')
    INSTR.write('WAV:SWE:TIME 16ms')
    INSTR.write('INIT:IMM;*WAI')
    INSTR.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')

    try:
        process_schedule()
        INSTR.write('DISP:ENAB ON')
        logging.info("Schedule finished for the day.\n")
    except Exception as e:
        logging.info(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
