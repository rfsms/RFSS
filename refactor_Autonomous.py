from RsInstrument import RsInstrument, RsInstrException, LoggingMode
import time
import datetime
import os 
import tarfile
import glob
import subprocess
import csv
import pytz

# Constants
CSV_FILE_PATH = "/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv"
SOURCE_DIRECTORY = "/home/noaa_gms/RFSS/Received"
REMOTE_IP = "noaa-gms-ec2"
REMOTE_USERNAME = "Administrator"
REMOTE_PATH = "/"
RESOURCE_STRING_1 = 'TCPIP::192.168.1.101::hislip0'
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
UTC = pytz.UTC

def parse_utc_time(utc_time_str):
    return datetime.datetime.strptime(utc_time_str, '%m/%d/%Y %H:%M:%S')

# Function to get contents of c:\R_S\Instr\user\RFSS\ on Spectrum Analyzer download locally to /home/noaa_gms/RFSS/Received 
# These files will be called something like "NOAA15_2023-08-02_19_00_07_UTC.iq.tar"
# Deletion needs to be added here as it currently exists outside this function at the bottom - (instr.write('MMEM:DEL "c:\\R_S\\Instr\\user\\RFSS\\*"')) and its ugly
def get_SpecAn_content_and_DL_locally(instr):
    try:
        # Set the current directory
        instr.write('MMEM:CDIR "c:\\R_S\\Instr\\user\\RFSS\\"')

        # List the directory content
        response = instr.query('MMEM:CAT?')

        # Process the response and print the content
        content_list = response.replace('\'', '').split(',')
        print("Transferring captures from Spectrum Analyzer to process on RFSS server.")
        for item in content_list:
            print(item)

            # Download each file in the directory (skip directories)
            if not item.endswith('/'):  # Skip directories
                local_filename = '/home/noaa_gms/RFSS/Received/' + item  # Set the destination path on your PC
                instrument_filename = 'c:\\R_S\\Instr\\user\\RFSS\\' + item  # Set the instrument file path

                try:
                    # Download the file
                    data = instr.read_file_from_instrument_to_pc(instrument_filename, local_filename)

                    # Check if data is not None before writing to the file
                    if data is not None:
                        with open(local_filename, 'wb') as f:
                            f.write(data)
                        print(f"Downloaded file '{item}' to '{local_filename}'")
                    else:
                        #print('')
                        continue

                except Exception as e:
                    print(f"Error while downloading file '{item}': {str(e)}")

        print('Removing files from Spectrum Analyzer')    
        instr.write('MMEM:DEL "c:\\R_S\\Instr\\user\\RFSS\\*"')
    
    except RsInstrException as e:
        if "-256," in str(e):
            print("No files on Spectrum Analyzer to process:", e)
            
# Function to tar.gz all files in /home/noaa_gms/RFSS/Received/* with a satName_timestamp and then delete all *.iq.tar.  Then scp all files to E2 using the scp function
# These files will be called someting like "NOAA15_2023-08-02_19_00_00_UTC.tar.gz" and will be comprised of the above *.iq.tar files
# Need to make this cleaner so SCP function isnt called internally, but leaving now for 
def local_tgz_and_rm_IQ(directory, satellite):

    current_datetime = datetime.datetime.utcnow()
    formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC')
    
    # Get a list of all files in the directory
    all_files = [os.path.join(directory, file) for file in os.listdir(directory)]

    # Check if there are any files to archive
    if not all_files:
        print(f"No files found in '{directory}'. Skipping tar.gz creation.")
        return

    # Create the name of the final tar.gz file
    gz_file = os.path.join(directory, f'{satellite}_{formatted_current_datetime}.tar.gz')

    # Create the tar.gz archive
    with tarfile.open(gz_file, 'w:gz') as tar:
        for file in all_files:
            tar.add(file, arcname=os.path.basename(file))
    
    # Remove the original files
    for file in all_files:
        os.remove(file)

    # Check if the gz_file exists before proceeding
    if os.path.exists(gz_file):
        print('Executing SCP of *.tar.gz files and removing locally')
        scp_tgz_files_and_delete(SOURCE_DIRECTORY, REMOTE_IP, REMOTE_USERNAME, REMOTE_PATH)
    else:
        print(f"No '{gz_file}' found. Skipping scp_gz_files_and_delete.")

# Function to scp anything called tar.gz (created by from local_tar_gz_and_rm_IQ_tar function) in /home/noaa_gms/RFSS/Received/, then delete *.tar.gz's to clean up.
# This should probably be cleaned up as well
# Need to also add some error control in case ec2 intance is not up we i.e dont wait and dont delete the tar.gz files.
def scp_tgz_files_and_delete(source_dir, remote_ip, remote_username, remote_path):
    try:
        # List all tar.gz files in the source directory
        file_list = glob.glob(os.path.join(source_dir, '*tar.gz'))

        if not file_list:
            print("No *.tar.gz files found in the source directory.")
            return

        # Construct the scp command
        scp_cmd = [
            'scp',
            '-r', 
            *file_list,
            f'{remote_username}@{remote_ip}:{remote_path}'
        ]

        # Run the scp command using subprocess and capture stdout and stderr
        process = subprocess.Popen(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Process and print the progress
        for line in process.stderr:
            if line.startswith('Sending'):
                print(line.strip())

        # Wait for the process to complete
        process.wait()

        print("All .tar.gz files successfully copied to the remote EC2 server.")

        # Delete the files from the source directory
        for file_path in file_list:
            os.remove(file_path)

        print("All .tar.gz files deleted locally from the RFSS source directory.")
    except subprocess.CalledProcessError as e:
        print("Error while copying files:", e)

def load_schedule_from_csv(csv_file_path):
    utc_schedule = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the first line (header)
        for row in reader:
            entry = int(row[0])
            start_time_str = row[1].strip('()').split(', ')
            start_time = datetime.time(int(start_time_str[0]), int(start_time_str[1]), int(start_time_str[2]))
            end_time_str = row[2].strip('()').split(', ')
            end_time = datetime.time(int(end_time_str[0]), int(end_time_str[1]), int(end_time_str[2]))
            label = row[3]
            utc_schedule.append((entry, start_time, end_time, label))
    return sorted(utc_schedule, key=lambda entry: entry[1])

def main():
    instr = RsInstrument(RESOURCE_STRING_1, False, False, OPTION_STRING_FORCE_RS_VISA)
    print('setting up instr')
    instr.reset()
    instr.clear_status()
    instr.write("SYST:DISP:UPD ON")
    instr.write("INIT:CONT ON")
    instr.write("SENS:FREQ:CENT 1702500000")
    instr.write("SENS:FREQ:SPAN 20000000")
    instr.write("SENS:BAND:RES 10000")
    instr.write("SENS:BAND:VID:AUTO OFF")
    instr.write("SENS:BAND:VID 50")
    instr.write("INP:ATT:AUTO OFF")
    instr.write("INP:ATT 0")
    instr.write("DISP:WIND1:SUBW:TRAC1:MODE AVER")
    instr.write("SENS:WIND1:DET1:FUNC RMS")
    instr.write("DISP:WIND1:SUBW:TRAC2:MODE MAXH")
    instr.write("SENS:WIND1:DET2:FUNC RMS")
    instr.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL 100")
    instr.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110")
    instr.write("CALC1:SGR:STAT ON")
    instr.write("INST:CRE:NEW IQ, 'IQ Analyzer'")
    instr.write("INIT:CONT OFF")
    instr.write("TRAC:IQ:SRAT 18750000")
    instr.write("SENS:SWE:TIME 0.016")
    instr.write("SENS:SWE:COUN 10")
    instr.write("HCOP:DEV:LANG PNG")

    utc_schedule = load_schedule_from_csv(CSV_FILE_PATH)

    try:
        has_functions_executed = False
        while True:
            now = datetime.datetime.now(tz=UTC)
            current_day = now.weekday()

            # Extract the day, start time, and end time from the first schedule entry
            first_entry_day, first_entry_start, first_entry_end, first_entry_satellite = utc_schedule[0]

            for day, start, end, satellite in utc_schedule:

                if current_day == day and start <= now.time() <= end:
                    
                    #Setup timestamps for filenames
                    current_datetime = datetime.datetime.utcnow()
                    formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                    time_saved_IQ = f"'C:\\R_S\\Instr\\user\RFSS\{satellite}_{formatted_current_datetime}'"
                        
                    instr.write("INST IQ")
                    instr.write("INIT:IMM;*WAI")
                    # print('Waiting for 10 IQ sweeps...')

                    instr.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
                    # instr.write("INST:SEL 'Spectrum'")

                    # instr.write("INIT:CONT ON")
                    print(f"Current IQ save filename is: {time_saved_IQ}")
                    print(f"Function with label '{satellite}' is running!")
                
            # If the current time has surpassed the end time of the first entry and the functions haven't executed yet
            if current_day == day and start <= now.time() <= first_entry_end:                
                get_SpecAn_content_and_DL_locally(instr)
                local_tgz_and_rm_IQ(directory=SOURCE_DIRECTORY)
                has_functions_executed = True
                
            # If the current time has surpassed the end time of the first entry, remove it from the schedule
            if current_day == first_entry_day and now.time() > first_entry_end:
                utc_schedule.pop(0)
                has_functions_executed = False  # 

            time.sleep(5)

    except KeyboardInterrupt:
        print("User killed it.")

    instr.close()

if __name__ == "__main__":
    main()
