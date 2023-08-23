#!/usr/bin/env python3
from RsInstrument import RsInstrument, RsInstrException, LoggingMode
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

# # For development
# CSV_FILE_PATH = '/home/noaa_gms/RFSS/Backup_Testing/schedule.csv'
# For production
CSV_FILE_PATH = '/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv'
TEMP_DIR = '/home/noaa_gms/RFSS/Received/'
REMOTE_IP = 'noaa-gms-ec2'
REMOTE_USERNAME = 'Administrator'
REMOTE_PATH = '/'
RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0'
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
INSTR = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
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

    # Check if there are any files to archive
    if not all_files:
        logging.info(f"No files found in '{directory}'. Skipping tar.gz creation.")
        return

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
    else:
        logging.info(f"No '{gz_file}' found. Skipping scp_gz_files_and_delete.")

# Function to get contents of c:\R_S\Instr\user\RFSS\ on Spectrum Analyzer download locally to /home/noaa_gms/RFSS/Received 
# These files will be called something like "2023-08-02_19_00_07_UTC_NOAA-15.iq.tar"
def get_SpecAn_content_and_DL_locally(INSTR):
    try:
        # Set and list the current directory on the SA
        INSTR.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = INSTR.query('MMEM:CAT?')

        # Process the response and print the content
        content_list = response.replace('\'', '').split(',')
        logging.info("Transferring captures from Spectrum Analyzer to process on RFSS server.")
        for item in content_list:
            logging.info(item)

            # Download each file in the directory (skip directories)
            if not item.endswith('/'):  # Skip directories
                temp_filename = TEMP_DIR + item  # Set the destination path on your PC
                # print(f'temp filename: {temp_filename}')
                instrument_filename = INSTR_DIR + item  # Set the SA file path
                # print(f'instrument filename: {instrument_filename}')

                try:
                    # Download the file
                    data = INSTR.read_file_from_instrument_to_pc(instrument_filename, temp_filename)

                    # Check if data is not None before writing to the file
                    if data is not None:
                        with open(temp_filename, 'wb') as f:
                            f.write(data)
                            # print(f"Downloaded file '{item}' to '{temp_filename}'")
                    else:
                        #print('')
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
                time.sleep(1)  # Sleep for 5 seconds to not hog the CPU
                # print('Waiting for next schedule')
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
                INSTR.write('INST IQ')
                INSTR.write('INIT:IMM;*WAI')
                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                time_saved_IQ = f"'{INSTR_DIR}{formatted_current_datetime}_{satellite_name}'"
                # print(f'To Be saved: {time_saved_IQ}')
                INSTR.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
                # print('Waiting for 10 IQ sweeps...')
                time.sleep(1)  # Sleep for 1 second
            
            # # print_message(satellite_name)
            get_SpecAn_content_and_DL_locally(INSTR)
            local_tgz_and_rm_IQ(TEMP_DIR, satellite_name)

def main():

    # Instrument reset/setup
    logging.info(f'Setting Up Instrument at {RESOURCE_STRING}')
    # INSTR = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
    INSTR.reset()
    INSTR.clear_status()
    INSTR.write('SYST:DISP:UPD ON')
    INSTR.write('INIT:CONT ON')
    INSTR.write('SENS:FREQ:CENT 1702500000')
    INSTR.write('SENS:FREQ:SPAN 20000000')
    INSTR.write('SENS:BAND:RES 10000')
    INSTR.write('SENS:BAND:VID:AUTO OFF')
    INSTR.write('SENS:BAND:VID 50')
    INSTR.write('INP:ATT:AUTO OFF')
    INSTR.write('INP:ATT 0')
    INSTR.write('DISP:WIND1:SUBW:TRAC1:MODE AVER')
    INSTR.write('SENS:WIND1:DET1:FUNC RMS')
    INSTR.write('DISP:WIND1:SUBW:TRAC2:MODE MAXH')
    INSTR.write('SENS:WIND1:DET2:FUNC RMS')
    INSTR.write('DISP:WIND1:SUBW:TRAC1:Y:SCAL 100') 
    INSTR.write('DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110')
    INSTR.write('CALC1:SGR:STAT ON')
    INSTR.write("INST:CRE:NEW IQ, 'IQ Analyzer'")
    INSTR.write('INIT:CONT OFF')
    INSTR.write('TRAC:IQ:SRAT 18750000')
    INSTR.write('SENS:SWE:TIME 0.016')
    INSTR.write('SENS:SWE:COUN 10')
    INSTR.write('HCOP:DEV:LANG PNG')

    try:
        # # Create schedule for debug - Will need to comment out once moved to production
        # # This sets up schedule for testing where only thing to input is num_of_entries in the schedule.csv
        # # For entries, you can modify start_times/end_times to reflect a larger or smaller window between "passes"
        # num_of_entries = 2

        # # Delay the first entry by 20 seconds (now + 20), 
        # # a pass duration of 10 seconds (event) - (can be modified to 60s to test an overload scenario of overlapping passes))
        # # And a wait duration between (gap) of 20 seconds (can be modified to 1s to test an overload scenario of overlapping passes)
        # now = datetime.datetime.utcnow() + datetime.timedelta(seconds=20)  
        # event_duration = datetime.timedelta(seconds=10)
        # gap_duration = datetime.timedelta(seconds=20)
        # total_duration = event_duration + gap_duration

        # start_times = [(now + i*total_duration) for i in range(num_of_entries)]
        # end_times = [(now + i*total_duration + event_duration) for i in range(num_of_entries)]

        # with open("/home/noaa_gms/RFSS/Backup_Testing/schedule.csv", "w") as f:
        #     writer = csv.writer(f)
        #     writer.writerow(["Day of Week", "AOS", "LOS", "Satellite"])
        #     # Corner case to add an initial entry that has already past in case the app needs to be restarted
        #     writer.writerow([1, "(19, 59, 23)", "(20, 0, 23)", "PAST ENTRY"])
        #     for i in range(num_of_entries):
        #         writer.writerow([now.weekday() + 1, 
        #                         str((start_times[i].hour, start_times[i].minute, start_times[i].second)), 
        #                         str((end_times[i].hour, end_times[i].minute, end_times[i].second)), 
        #                         f"NOAA-{15 + i}"])
        # # End debug section

        process_schedule()
        logging.info("Schedule finished for the day.\n")
    except Exception as e:
        logging.info(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
