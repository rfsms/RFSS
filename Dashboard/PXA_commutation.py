import pyvisa
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy.io import savemat
import logging

# Reset the Root Logger - this section is used to reset the root logger and then apply below configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initialize logger
logger = logging.getLogger(__name__)

RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0' 
RM = pyvisa.ResourceManager()
PXA = RM.open_resource(RESOURCE_STRING, timeout = 20000)
TEMP_DIR = '/home/noaa_gms/RFSS/Received/'

def check_instrument_state():
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
    except Exception as e:
        logging.info(f"An error occurred in instrument setup: {e}")

# def captureTrace(set_az):
def captureTrace(iq, set_az, band):
    try:
        PXA.write("INST:SCR:SEL 'Spectrum Analyzer 1'")
        PXA.write("INIT:IMM;*WAI")
        # Removing this section since Agilnet apparently doesnt know how to handle OPC correctly...
        # if PXA.query('*OPC?') == '1':
        #     print(f"OPC is good")
        #     trace_data = PXA.query('TRAC? TRACE1')
        #     return trace_data
        trace_data = PXA.query('TRAC? TRACE2')
    
        if iq:
        # logging.info(f'starting IQ with band: {band}')
            PXA.write("INST IQ")
            if band == 'AWS1':
                PXA.write('TRAC:IQ:SRAT 12500000')  # For 10Mhz ABW
            elif band == 'AWS3':
                PXA.write('TRAC:IQ:SRAT 6250000')  # For 5Mhz ABW
            else:
                logging.error(f"Invalid band selection: {band}")
                return None
 
            PXA.write("INIT:IMM;*WAI")
            # opc_result_iq = PXA.query('*OPC?')
            # if opc_result_iq != '1':
            #     logging.error(f"IQ data not stored (*OPC? returned '{opc_result_iq}' after setting to IQ)")
            #     return None
            data = PXA.query_binary_values(":FETCH:WAV0?")
                            # Convert to separate I and Q arrays
            i_data = data[::2]
            q_data = data[1::2]

            # Save I/Q data to MAT file
            savemat(f'{TEMP_DIR}{set_az}.mat', {'I_Data': i_data, 'Q_Data': q_data})

            time_saved_IQ = f"'{set_az}'"
            PXA.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")

        return trace_data
    
    except Exception as e:
        logging.error(f"An error occurred during captureTrace: {e}")
        return None
    