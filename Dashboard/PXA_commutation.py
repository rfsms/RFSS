import pyvisa
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy.io import savemat

TEMP_DIR = '/home/noaa_gms/RFSS/Received/'
RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0' 
RM = pyvisa.ResourceManager()
PXA = RM.open_resource(RESOURCE_STRING, timeout = 20000)
INSTR_DIR = 'c:\\R_S\\Instr\\user\\RFSS\\'

def createSpectrogram(dirDate, csv_file_path, start_frequency_mhz, end_frequency_mhz, starting_az, ending_az, location):
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
    plt.title(f"Start Freq: {start_frequency_mhz} MHz, Stop Freq: {end_frequency_mhz} MHz\nStart AZ: {starting_az}, Stop AZ: {ending_az}\n{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')} UTC - {location}")
    plt.tight_layout()
    plt.savefig(os.path.join(dirDate, f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'))
    plt.close()

def instrument_scanning_setup():
    # For MXA (without IQ, no need to change anything...will need to modify once we add IQ extract)
    PXA.write("INST:SCR:SEL 'IQ Analyzer 1'")
    # PXA.write("SENS:SWE:WIND1:POIN 1001")
    # PXA.write("SENS:FREQ:CENT 1702.5MHz")
    # PXA.write('SENS:FREQ:SPAN 8MHz')
    # PXA.write("INST IQ")

def instrument_commutation_setup(center_frequency_MHz=1702.5, span_MHz=20, points=1001):
    try:

        # PXA.visa_timeout = 20000
        PXA.write("INST:SCR:SEL 'Spectrum Analyzer 1'")
        PXA.write(f"SENS:FREQ:CENT {center_frequency_MHz}MHz")
        PXA.write(f"SENS:FREQ:SPAN {span_MHz}MHz")
        PXA.write(f"SWE:POIN {points}")

    except KeyboardInterrupt:
        print(f"An error occurred in instrument setup")

# def captureTrace(set_az):
def captureTrace():
    try:
        PXA.write("INIT:IMM")
        # Removing this section since Agilnet apparently doesnt know how to handle OPC correctly...
        # if PXA.query('*OPC?') == '1':
        #     print(f"OPC is good")
        #     trace_data = PXA.query('TRAC? TRACE1')
        #     return trace_data
        trace_data = PXA.query('TRAC? TRACE2')
        return trace_data
        # PXA.write("INST IQ")
        # PXA.write("INIT:IMM")
        # if PXA.query('*OPC?') == '1':
        #     current_datetime = datetime.datetime.utcnow()
        #     formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC')
        #     time_saved_IQ = f"'{INSTR_DIR}{set_az}_{formatted_current_datetime}'"
        #     PXA.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")
        #     get_SpecAn_content_and_DL_locally(PXA)
    except KeyboardInterrupt:
        print("Manually stopped by user.")
    