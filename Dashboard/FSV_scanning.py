from RsInstrument import RsInstrument, RsInstrException
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy.io import savemat

TEMP_DIR = '/home/noaa_gms/RFSS/Received/'
RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0'
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
FSV = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
INSTR_DIR = 'c:\\R_S\\Instr\\user\\RFSS\\'

def createSpectrogram(dirDate, csv_file_path, start_frequency_mhz, end_frequency_mhz, starting_az, ending_az):
    df = pd.read_csv(csv_file_path)
    frequencies = df['Frequency (MHz)']
    timestamps = df.columns[1:]
    data = df.iloc[:, 1:].to_numpy()

    plt.figure(figsize=(20, 10))
    
    plt.imshow(data, aspect='auto', cmap='viridis', origin='lower',
               extent=[0, len(timestamps) - 1, frequencies.iloc[0], frequencies.iloc[-1]],
               vmin=-140, vmax=-40)
    plt.colorbar(label='Amplitude (dB)')
    plt.xticks(range(len(timestamps)), timestamps, rotation=45, ha="right", rotation_mode="anchor")
    plt.yticks(np.arange(frequencies.iloc[0], frequencies.iloc[-1], step=0.5))
    plt.xlabel('Timestamp')
    plt.ylabel('Frequency (MHz)')
    plt.xticks(range(0, len(timestamps), 2), timestamps[::2], rotation=45, ha="right", rotation_mode="anchor") # Every two ticks
    # plt.xticks(range(0, len(timestamps), 5), timestamps[::5], rotation=45, ha="right", rotation_mode="anchor") # Every 5 ticks
    plt.title(f"Start Freq: {start_frequency_mhz} MHz, Stop Freq: {end_frequency_mhz} MHz\nStart AZ: {starting_az}, Stop AZ: {ending_az}\n{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')} UTC")
    plt.tight_layout()
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

def instrument_pass_setup():
    FSV.write('INST IQ')

def instrument_scan_setup(center_frequency_mhz, span_mhz):
    try:
        # print("Attempting instrument setup")
        FSV.reset()
        FSV.clear_status()
        FSV.visa_timeout = 20000
        FSV.write("SYST:DISP:UPD ON")
        FSV.write("INIT:CONT ON")
        FSV.write(f"SENS:FREQ:CENT {center_frequency_mhz}MHz")
        FSV.write(f"SENS:FREQ:SPAN {span_mhz}MHz")
        FSV.write("SENS:BAND:RES 5000")
        FSV.write("SENS:BAND:VID:AUTO OFF")
        FSV.write("SENS:BAND:VID 5000")
        FSV.write("INP:ATT:AUTO OFF")
        FSV.write("INP:ATT 0")
        FSV.write("DISP:WIND:SUBW:TRAC:Y:SCAL:RLEV -30")
        FSV.write("DISP:WIND1:SUBW:TRAC1:MODE AVER")
        FSV.write("SENS:WIND1:DET1:FUNC RMS")
        FSV.write("DISP:WIND1:SUBW:TRAC2:MODE MAXH")
        FSV.write("SENS:WIND1:DET2:FUNC RMS")
        FSV.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL 100") 
        FSV.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110")
        FSV.write("SENS:SWE:COUN 20")
        FSV.write("INST:CRE:NEW IQ, 'IQ Analyzer'")
        FSV.write("INIT:CONT OFF")
        FSV.write("TRAC:IQ:SRAT 6250000") # For 5MHz channel
        FSV.write("SENS:SWE:TIME 0.016")
        FSV.write("SENS:SWE:COUN 10")
        FSV.write("HCOP:DEV:LANG PNG")
        FSV.write("INST:SEL 'Spectrum'")
        print("Instrument Setup Complete")
    except KeyboardInterrupt:
        print(f"An error occurred in instrument setup")

# def captureTrace(set_az):
def captureTrace():
    try:
        FSV.write("INIT:IMM")
        if FSV.query('*OPC?') == '1':
            trace_data = FSV.query('TRAC? TRACE1')
            # print(trace_data)
            return trace_data

        # FSV.write("INST IQ")
        # FSV.write("INIT:IMM")
        # if FSV.query('*OPC?') == '1':
        #     current_datetime = datetime.datetime.utcnow()
        #     formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC')
        #     time_saved_IQ = f"'{INSTR_DIR}{set_az}_{formatted_current_datetime}'"
        #     FSV.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
        #     get_SpecAn_content_and_DL_locally(FSV)
    except KeyboardInterrupt:
        print("Manually stopped by user.")