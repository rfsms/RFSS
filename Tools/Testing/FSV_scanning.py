from RsInstrument import RsInstrument, RsInstrException
import time
import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import pandas as pd
from scipy.io import savemat
import subprocess
import sys

TEMP_DIR = '/home/noaa_gms/RFSS/Received/'
RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0'
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
INSTR = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
INSTR_DIR = 'c:\\R_S\\Instr\\user\\RFSS\\'

manualDir = '/home/noaa_gms/RFSS/Tools/Testing/manualCaptures'

# Specify the center frequency in MHz, span in MHz, and number of points collected
center_frequency_mhz = 1702500000  # Center frequency in MHz
span_mhz = 6000000  # Span in MHz
num_points = 1001 # Replace with the number of points collected

# Calculate the frequency values in MHz with four decimal places
frequency_start_mhz = (center_frequency_mhz/1000000) - span_mhz / 2
frequency_step_mhz = (span_mhz/100000) / (num_points - 1)
frequency_values_mhz = [round(frequency_start_mhz + i * frequency_step_mhz, 4) for i in range(num_points)]

# Generate a unique folder name based on current time and create the folder if it doesnt exist
folderDate = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
dirDate = os.path.join(manualDir, folderDate)
os.makedirs(dirDate)

def createSpectrogram(dirDate, timestamp_str, csv_file_path):
    df = pd.read_csv(csv_file_path)
    frequencies = df['Frequency (MHz)']
    timestamps = df.columns[1:]
    data = df.iloc[:, 1:].to_numpy()
    all_data = data.T  # Transpose the data array
    all_timestamps = np.array(timestamps)

    plt.figure(figsize=(10, 6))
    
    if all_data.shape[0] == 1:
        plt.plot(frequencies, all_data[0, :])
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Amplitude (dB)')
    else:
        plt.imshow(all_data, aspect='auto', cmap='viridis', origin='lower',
            extent=[frequencies.iloc[0], frequencies.iloc[-1], 0, len(all_timestamps)-1],
            vmin=-140, vmax=-40)
        plt.colorbar(label='Amplitude (dB)')
        plt.yticks(range(len(all_timestamps)), all_timestamps)
        plt.xlabel('Frequency (MHz)')
        
    plt.title(f'{timestamp_str} UTC')
    plt.savefig(os.path.join(dirDate, f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'))
    plt.close()

def get_SpecAn_content_and_DL_locally(INSTR):
    try:
        # Set and list the current directory on the SA
        INSTR.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = INSTR.query('MMEM:CAT?')

        # Process the response and log the content
        content_list = response.replace('\'', '').split(',')
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
                    print(f"Error while downloading file '{item}': {str(e)}")

        print('Removing files from Spectrum Analyzer')    
        INSTR.write(f'MMEM:DEL "{INSTR_DIR}*"')

    except RsInstrException as e:
        if "-256," in str(e):
            print("No files on Spectrum Analyzer to process:", e)        

def instrument_setup(center_frequency_mhz, span_mhz):
    try:
        INSTR.reset()
        INSTR.clear_status()
        INSTR.visa_timeout = 20000
        INSTR.write("SYST:DISP:UPD ON")
        INSTR.write("INIT:CONT ON")
        INSTR.write(f"SENS:FREQ:CENT {center_frequency_mhz}")
        INSTR.write(f"SENS:FREQ:SPAN {span_mhz}")
        INSTR.write("SENS:BAND:RES 5000")
        INSTR.write("SENS:BAND:VID:AUTO OFF")
        INSTR.write("SENS:BAND:VID 5000")
        INSTR.write("INP:ATT:AUTO OFF")
        INSTR.write("INP:ATT 0")
        INSTR.write("DISP:WIND:SUBW:TRAC:Y:SCAL:RLEV -30")
        INSTR.write("DISP:WIND1:SUBW:TRAC1:MODE AVER")
        INSTR.write("SENS:WIND1:DET1:FUNC RMS")
        INSTR.write("DISP:WIND1:SUBW:TRAC2:MODE MAXH")
        INSTR.write("SENS:WIND1:DET2:FUNC RMS")
        INSTR.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL 100") 
        INSTR.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110")
        INSTR.write("SENS:SWE:COUN 10")
        INSTR.write("INST:CRE:NEW IQ, 'IQ Analyzer'")
        INSTR.write("INIT:CONT OFF")
        INSTR.write("TRAC:IQ:SRAT 6250000") # For 5MHz channel
        INSTR.write("SENS:SWE:TIME 0.016")
        INSTR.write("SENS:SWE:COUN 10")
        INSTR.write("HCOP:DEV:LANG PNG")
        INSTR.write("INST:SEL 'Spectrum'")
    except KeyboardInterrupt:
        print("Manually stopped by user.")

def captureTrace(set_az):
    try:
        INSTR.write("INIT:IMM")
        if INSTR.query('*OPC?') == '1':
            trace_data = INSTR.query('TRAC? TRACE1')
            print(trace_data)

        INSTR.write("INST IQ")
        INSTR.write("INIT:IMM")
        if INSTR.query('*OPC?') == '1':
            current_datetime = datetime.datetime.utcnow()
            formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC')
            time_saved_IQ = f"'{INSTR_DIR}{set_az}_{formatted_current_datetime}'"
            INSTR.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
            get_SpecAn_content_and_DL_locally(INSTR)
    except KeyboardInterrupt:
        print("Manually stopped by user.")


captureTrace(80)