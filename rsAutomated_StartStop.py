# RFSS VNA Setup and Execution 
# Code setup both Spectrum and IQ instruments, capture screenshot of spectrum analyzer (with spectrogram), move to IQ instrument, run 10 sweeps and then capture IQ data.
# Data is then saved with UTC YMDhms timestamp
# API Reference
# https://rsinstrument.readthedocs.io/en/latest/StepByStepGuide.html
# Preconditions:
# - Installed RsInstrument Python module from pypi.org
# https://www.rohde-schwarz.com/us/faq/how-to-install-update-rsinstrument-package-faq_78704-946496.html
# - Installed VISA e.g. R&S Visa 5.12.x or newer
# https://www.rohde-schwarz.com/us/applications/r-s-visa-application-note_56280-148812.html

from RsInstrument import * 
import time
import datetime
import os 
import tarfile
import glob
import subprocess

resource_string_1 = 'TCPIP::192.168.1.101::hislip0'  

option_string_force_rs_visa = 'SelectVisa=rs'  # Forcing R&S VISA usage

# Make sure you have the last version of the RsInstrument
RsInstrument.assert_minimum_version('1.53.0')

#SCP Setup - using preshared ECDSA keys with 521 bit curve (1024 bytes...for the curious 😂)
source_directory = "/home/noaa_gms/RFSS/Received"
remote_ip = "noaa-gms-ec2"
remote_username = "Administrator"
remote_path = "/"

# Function to convert UTC string/UTC for scheduling/filenames/etc..
def parse_utc_time(utc_time_str):
    return datetime.datetime.strptime(utc_time_str, '%m/%d/%Y %H:%M:%S')

# Function to get contents of c:\R_S\Instr\user\RFSS\ on Spectrum Analyzer download locally to /home/noaa_gms/RFSS/Received 
# These files will be called something like "NOAA15_2023-08-02_19_00_07_UTC.iq.tar"
# Deletion needs to be added here as it currently exists outside this function at the bottom - (instr.write('MMEM:DEL "c:\\R_S\\Instr\\user\\RFSS\\*"')) and its ugly
def get_SpecAn_content_and_DL_locally():
    try:

        # Set the current directory
        instr.write('MMEM:CDIR "c:\\R_S\\Instr\\user\\RFSS\\"')

        # List the directory content
        response = instr.query('MMEM:CAT?')

        # Process the response and print the content
        content_list = response.replace('\'', '').split(',')
        print("Removing captures from Spectrum Analyzer to process on RFSS server.")
        for item in content_list:
            #print(item)

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
                        #print(f"Downloaded file '{item}' to '{local_filename}'")
                    else:
                        #print('')
                        continue

                except Exception as e:
                    print(f"Error while downloading file '{item}': {str(e)}")

    except Exception as e:
        print(f"Error: {str(e)}")

# Function to tar.gz all files in /home/noaa_gms/RFSS/Received/* with a satName_timestamp and then delete all *.iq.tar.  Then scp all files to E2 using the scp function
# These files will be called someting like "NOAA15_2023-08-02_19_00_00_UTC.tar.gz" and will be comprised of the above *.iq.tar files
# Need to make this cleaner so SCP function isnt called internally, but leaving now for 
def local_tgz_and_rm_IQ(directory):
    # Get a list of all files in the directory
    all_files = [os.path.join(directory, file) for file in os.listdir(directory)]

    # Create the name of the final tar.gz file
    gz_file = os.path.join(directory, f'{satName}_{formatted_UTC_time_str}.tar.gz')

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
        scp_tgz_files_and_delete(source_directory, remote_ip, remote_username, remote_path)
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

if __name__ == "__main__":

    #Current semi automated working sample example where start/stop/satName is defined and the code will execute only between start/stop times
    global formatted_UTC_time_str
    global satName

    #This is really the only section that needs to be adjusted to run between start-stop
    UTC_start_time_str = '8/07/2023 18:15:00'
    UTC_stop_time_str = '8/07/2023 18:15:30'
    satName = "NOAA15"

    UTC_start_time = parse_utc_time(UTC_start_time_str)
    UTC_stop_time = parse_utc_time(UTC_stop_time_str)
    formatted_UTC_time_str = UTC_start_time.strftime('%Y-%m-%d_%H_%M_%S_UTC')

    try:
        print('Preparing Instrument')
        instr = RsInstrument(resource_string_1, False, False, option_string_force_rs_visa) #(Resource, ID Query, Reset, Options)

        # Switch ON logging to the console for troubleshooting SpecAn config issues
        # instr.logger.log_to_console = True
        # instr.logger.mode = LoggingMode.On

        # Instrument Setup
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

        while datetime.datetime.utcnow() < UTC_stop_time:
            if datetime.datetime.utcnow() >= UTC_start_time:

                #Setup timestamps for filenames
                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 

                time_saved_IQ = f"'C:\\R_S\\Instr\\user\RFSS\{satName}_{formatted_current_datetime}'"
                
                instr.write("INST IQ")
                instr.write("INIT:IMM;*WAI")
                print('Waiting for 10 IQ sweeps...')

                instr.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
                instr.write("INST:SEL 'Spectrum'")
                instr.write("INIT:CONT ON")
                print(f"Current IQ save filename is: {time_saved_IQ}")

            else:
                instr.write("INST:SEL 'Spectrum'")
                instr.write("INIT:CONT ON")
                print('Waiting for start time...')

            time.sleep(5)

    except KeyboardInterrupt:
        print("User killed it.")

    get_SpecAn_content_and_DL_locally()
    local_tgz_and_rm_IQ('/home/noaa_gms/RFSS/Received/')

    
# After succesful record and transfer, delete all remote files and close the session
instr.write('MMEM:DEL "c:\\R_S\\Instr\\user\\RFSS\\*"')
instr.close()
