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

TEMP_DIR = '/home/noaa_gms/RFSS/Received/'

def createSpectrogram(dirDate, csv_file_path, start_frequency_mhz, end_frequency_mhz, starting_az, ending_az, location):
    df = pd.read_csv(csv_file_path)
    frequencies = df['Frequency (MHz)']
    timestamps = df.columns[1:]
    data = df.iloc[:, 1:].to_numpy()

    plt.figure(figsize=(20, 10))
    
    plt.imshow(data, aspect='auto', cmap='viridis', origin='lower',
               extent=[0, len(timestamps) - 1, frequencies.iloc[0], frequencies.iloc[-1]],
               vmin=-140, vmax=-40)
    plt.colorbar(label='Amplitude (dBm)')
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

def instrument_scanning_setup(instr):
    instr.write("INST:SCR:SEL 'IQ Analyzer 1'")
    instr.write("SENS:FREQ:CENT 1702500000")
    instr.write('WAV:SRAT 18.75MHz')
    instr.write("WAV:SWE:TIME 160ms")

def instrument_commutation_setup(instr, center_frequency_MHz=1702.5, span_MHz=20, points=1001):
    try:
        # PXA.visa_timeout = 20000
        instr.write("INST:SCR:SEL 'Spectrum Analyzer 1'")
        instr.write(f"SENS:FREQ:CENT {center_frequency_MHz}MHz")
        instr.write(f"SENS:FREQ:SPAN {span_MHz}MHz")
        instr.write(f"SWE:POIN {points}")
    except Exception as e:
        logging.info(f"An error occurred in instrument setup: {e}")

def captureTrace(instr, iq, set_az, band):
    try:
        instr.write("INST:SCR:SEL 'Spectrum Analyzer 1'")
        instr.write("INIT:IMM;*WAI")
        trace_data = instr.query('TRAC? TRACE2')
    
        if iq:
        # logging.info(f'starting IQ with band: {band}')
            instr.write("INST:SCR:SEL 'IQ Analyzer 1'")

            if band == 'AWS1': #For LTE test
                instr.write('WAV:SWE:TIME .016')
                instr.write('WAV:SRAT 56250000')  # 56.25MHz SR (for 45MH MeasBW)
            elif band == 'AWS3': # For 5G test
                instr.write('WAV:SRAT 6250000')  # For 5Mhz ABW (AOML/NHC)
            else:
                logging.error(f"Invalid band selection: {band}")
                return None
 
            instr.write("INIT:IMM;*WAI")
            data = instr.query_binary_values(":FETCH:WAV0?")
            
            # Convert to separate I and Q arrays
            i_data = data[::2]
            q_data = data[1::2]

            # Save I/Q data to MAT file
            iq_dir = '/home/noaa_gms/RFSS/toDemod/' + datetime.datetime.now().strftime("%Y_%m_%d")
            if not os.path.exists(iq_dir):
                os.makedirs(iq_dir)
            
            mat_file_path = os.path.join(iq_dir, f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}_UTC_MANUAL_AZ_{set_az}.mat')
            savemat(mat_file_path, {'I_Data': i_data, 'Q_Data': q_data})

        return trace_data
    
    except Exception as e:
        logging.error(f"An error occurred during captureTrace: {e}")
        return None
    