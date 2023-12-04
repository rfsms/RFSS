import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy.io import savemat
import logging
import time

TEMP_DIR = '/home/noaa_gms/RFSS/Received/'

def check_instrument_state(PXA):
    try:
        # Check the instrument's event status register to ensure no errors
        sesr = PXA.query("*ESR?")
        logging.info(f"Instrument SESR: {sesr}")

        # Check if the operation is complete
        opc = PXA.query("*OPC?")
        logging.info(f"Instrument Operation Complete: {opc}")
        
        # Check the status byte register
        stb = PXA.query("*STB?")
        logging.info(f"Instrument STB: {stb}")

    except Exception as e:
        logging.error(f"Error while checking instrument state: {e}")

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

def instrument_setup(PXA, RESOURCE_STRING):
    try:
        logging.info("Starting PXA Instrument Capture Setup")

        # Instrument reset/setup
        idn = PXA.query("*IDN?")
        instrument = idn.replace("Hello, I am: ", "")
        logging.info(f"Setting Up '{instrument}' at {RESOURCE_STRING}")
        
        #Reset SpecAn
        PXA.write("*RST")
        PXA.write("*CLS")
        PXA.write("SYST:DEF SCR")

        # Setup Spectrum Analyzer
        PXA.write("INST:NSEL 1")
        PXA.write("INIT:CONT OFF")
        PXA.write("SENS:FREQ:SPAN 20000000")
        PXA.write("SENS:FREQ:CENT 1702500000")
        # PXA.write("SENS:SWE:POIN 10")
        PXA.write("POW:ATT:AUTO OFF")
        PXA.write("POW:ATT 0")
        PXA.write("BAND 5000")
        PXA.write("DISP:WIND:TRAC:Y:RLEV -40dBm")
        PXA.write("TRAC1:TYPE WRIT")
        PXA.write("DET:TRAC1 NORM")
        PXA.write("TRAC2:TYPE MAXH")
        PXA.write("DET:TRAC2 POS")
        PXA.write("AVER:COUNT 10")
        #Create IQ window
        PXA.write("INST:SCR:CRE")
        PXA.write("INST:NSEL 8")
        PXA.write("CONF:WAV")
        PXA.write("SENS:FREQ:CENT 1702500000")
        PXA.write("POW:GAIN ON")
        PXA.write("WAV:SRAT 18.75MHz")
        PXA.write("WAV:SWE:TIME 160ms")
        PXA.write("DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON")
        PXA.write("FORM:BORD SWAP")
        PXA.write("FORM REAL,32")

        logging.info("Scanning setup complete")

    except Exception as e:
        logging.error(f"Error while setting up instrument for scanning: {e}")
        
def instrument_scanning_setup(PXA):
    # For MXA (without IQ, no need to change anything...will need to modify once we add IQ extract)
    PXA.write("INST:SCR:SEL 'IQ Analyzer 1'")
    # PXA.write("SENS:SWE:WIND1:POIN 1001")
    # PXA.write("SENS:FREQ:CENT 1702.5MHz")
    # PXA.write('SENS:FREQ:SPAN 8MHz')
    # PXA.write("INST IQ")

def instrument_commutation_setup(PXA, center_frequency_MHz=1702.5, span_MHz=20, points=1001):
    try:
        # PXA.visa_timeout = 20000
        PXA.write("INST:SCR:SEL 'Spectrum Analyzer 1'")
        PXA.write(f"SENS:FREQ:CENT {center_frequency_MHz}MHz")
        PXA.write(f"SENS:FREQ:SPAN {span_MHz}MHz")
        PXA.write(f"SWE:POIN {points}")
    except Exception as e:
        logging.info(f"An error occurred in instrument setup: {e}")

# def captureTrace(PXA, iq, set_az, band):
#     try:
#         PXA.write("INST:SCR:SEL 'Spectrum Analyzer 1'")
#         PXA.write("INIT:IMM;*WAI")
#         # Removing this section since Agilnet apparently doesnt know how to handle OPC correctly...
#         # if PXA.query('*OPC?') == '1':
#         #     print(f"OPC is good")
#         #     trace_data = PXA.query('TRAC? TRACE1')
#         #     return trace_data
#         trace_data = PXA.query('TRAC? TRACE2')
    
#         if iq:
#         # logging.info(f'starting IQ with band: {band}')
#             PXA.write("INST IQ")
#             if band == 'AWS1':
#                 PXA.write('TRAC:IQ:SRAT 12500000')  # For 10Mhz ABW
#             elif band == 'AWS3':
#                 PXA.write('TRAC:IQ:SRAT 6250000')  # For 5Mhz ABW
#             else:
#                 logging.error(f"Invalid band selection: {band}")
#                 return None
 
#             PXA.write("INIT:IMM;*WAI")
#             # opc_result_iq = PXA.query('*OPC?')
#             # if opc_result_iq != '1':
#             #     logging.error(f"IQ data not stored (*OPC? returned '{opc_result_iq}' after setting to IQ)")
#             #     return None
#             data = PXA.query_binary_values(":FETCH:WAV0?")
#                             # Convert to separate I and Q arrays
#             i_data = data[::2]
#             q_data = data[1::2]

#             # Save I/Q data to MAT file
#             savemat(f'{TEMP_DIR}{set_az}.mat', {'I_Data': i_data, 'Q_Data': q_data})

#             time_saved_IQ = f"'{set_az}'"
#             PXA.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")

#         return trace_data
    
#     except Exception as e:
#         logging.error(f"An error occurred during captureTrace: {e}")
#         return None
    
def captureTrace(PXA):
    try:
        PXA.write("INST:SCR:SEL 'Spectrum Analyzer 1'")
        PXA.write("INIT:IMM;*WAI")
        trace_data = PXA.query('TRAC? TRACE2')

        PXA.write("INST:SCR:SEL 'IQ Analyzer 1'")

        PXA.write("INIT:IMM;*WAI")
        data = PXA.query_binary_values(":FETCH:WAV0?")

        # Convert to separate I and Q arrays
        i_data = data[::2]
        q_data = data[1::2]

        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save I/Q data to MAT file
        savemat(f'{TEMP_DIR}{current_time}.mat', {'I_Data': i_data, 'Q_Data': q_data})

        return trace_data

    except Exception as e:
        logging.error(f"An error occurred during captureTrace: {e}")
        return None