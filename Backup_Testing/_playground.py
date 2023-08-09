from RsInstrument import RsInstrument, RsInstrException, LoggingMode
import csv
import time
import datetime
import os 
import tarfile
import glob
import subprocess

# For development
CSV_FILE_PATH = "/home/noaa_gms/RFSS/Backup_Testing/schedule.csv"
# For production
# CSV_FILE_PATH = "/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv"
TEMP_DIR = "/home/noaa_gms/RFSS/Received/"
REMOTE_IP = "noaa-gms-ec2"
REMOTE_USERNAME = "Administrator"
REMOTE_PATH = "/"
RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0'
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
INSTR = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
INSTR_DIR = 'c:\\R_S\\Instr\\user\\RFSS\\'

# # now availble globally for all functions
# now = datetime.datetime.utcnow()

# def print_message(satellite_name):
#     """Simple function to print a message."""
#     now = datetime.datetime.utcnow()
#     print(f'Message processed for {satellite_name} at LOS of {now.strftime("%Y-%m-%d %H:%M:%S")}!')

def get_SpecAn_content_and_DL_locally(INSTR):
    try:
        # Set and list the current directory on the SA
        INSTR.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = INSTR.query('MMEM:CAT?')

        # Process the response and print the content
        content_list = response.replace('\'', '').split(',')
        print("Transferring captures from Spectrum Analyzer to process on RFSS server.")
        for item in content_list:
            print(item)

            # Download each file in the directory (skip directories)
            if not item.endswith('/'):  # Skip directories
                temp_filename = TEMP_DIR + item  # Set the destination path on your PC
                print(f'temp filename: {temp_filename}')
                instrument_filename = INSTR_DIR + item  # Set the SA file path
                print(f'instrument filename: {instrument_filename}')

                try:
                    # Download the file
                    data = INSTR.read_file_from_instrument_to_pc(instrument_filename, temp_filename)

                    # Check if data is not None before writing to the file
                    if data is not None:
                        with open(temp_filename, 'wb') as f:
                            f.write(data)
                        print(f"Downloaded file '{item}' to '{temp_filename}'")
                    else:
                        #print('')
                        continue

                except Exception as e:
                    print(f"Error while downloading file '{item}': {str(e)}")

        print('Removing files from Spectrum Analyzer')    
        INSTR.write('MMEM:DEL "c:\\R_S\\Instr\\user\\RFSS\\*"')
    
    except RsInstrException as e:
        if "-256," in str(e):
            print("No files on Spectrum Analyzer to process:", e)

def process_schedule():
    """Process the schedule CSV."""
    with open(CSV_FILE_PATH, 'r') as csvfile:
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
                print(f"Function with label '{satellite_name}' is running!")
                INSTR.write("INST IQ")
                INSTR.write("INIT:IMM;*WAI")
                current_datetime = datetime.datetime.utcnow()
                formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                time_saved_IQ = f"'{INSTR_DIR}{formatted_current_datetime}_{satellite_name}'"
                # print(f'To Be saved: {time_saved_IQ}')
                INSTR.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
                # print('Waiting for 10 IQ sweeps...')
                time.sleep(1)  # Sleep for 1 second
            
            # print_message(satellite_name)
            get_SpecAn_content_and_DL_locally(INSTR)


def main():

    # Instrument reset/setup
    print(f'Setting Up Instrument at {RESOURCE_STRING}')
    # INSTR = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
    INSTR.reset()
    INSTR.clear_status()
    INSTR.write("SYST:DISP:UPD ON")
    INSTR.write("INIT:CONT ON")
    INSTR.write("SENS:FREQ:CENT 1702500000")
    INSTR.write("SENS:FREQ:SPAN 20000000")
    INSTR.write("SENS:BAND:RES 10000")
    INSTR.write("SENS:BAND:VID:AUTO OFF")
    INSTR.write("SENS:BAND:VID 50")
    INSTR.write("INP:ATT:AUTO OFF")
    INSTR.write("INP:ATT 0")
    INSTR.write("DISP:WIND1:SUBW:TRAC1:MODE AVER")
    INSTR.write("SENS:WIND1:DET1:FUNC RMS")
    INSTR.write("DISP:WIND1:SUBW:TRAC2:MODE MAXH")
    INSTR.write("SENS:WIND1:DET2:FUNC RMS")
    INSTR.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL 100")
    INSTR.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110")
    INSTR.write("CALC1:SGR:STAT ON")
    INSTR.write("INST:CRE:NEW IQ, 'IQ Analyzer'")
    INSTR.write("INIT:CONT OFF")
    INSTR.write("TRAC:IQ:SRAT 18750000")
    INSTR.write("SENS:SWE:TIME 0.016")
    INSTR.write("SENS:SWE:COUN 10")
    INSTR.write("HCOP:DEV:LANG PNG")

    try:
        # Create schedule for debug - Will need to comment out once moved to production
        # This sets up schedule for testing where only thing to input is num_of_entries in the schedule.csv
        # For entries, you can modify start_times/end_times to reflect a larger or smaller window between "passes"
        num_of_entries = 2

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
