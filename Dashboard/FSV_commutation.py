import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import logging

# Reset the Root Logger - this section is used to reset the root logger and then apply below configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initialize logger
logger = logging.getLogger(__name__)

INSTR_DIR = 'c:\\R_S\\Instr\\user\\RFSS\\'

def check_instrument_state(instr):
    try:
        # Check the instrument's event status register to ensure no errors
        sesr = instr.query("*ESR?")
        logging.info(f"Instrument SESR: {sesr}")

        # Check if the operation is complete
        opc = instr.query("*OPC?")
        logging.info(f"Instrument Operation Complete: {opc}")
        
        # Check the status byte register
        stb = instr.query("*STB?")
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

def get_SpecAn_content_and_DL_locally(instr, target_directory):
    try:

        check_instrument_state(instr)

        # Set and list the current directory on the SA
        instr.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = instr.query('MMEM:CAT?')
        logging.info(f'SA Response: {response}')

        # Process the response and log the content
        content_list = response.replace('\'', '').split(',')
        for item in content_list:
            # logging.info(item)

            # Download each file in the directory (skip directories)
            if not item.endswith('/'):  # Skip directories
                # temp_filename = dirDate + item  # Set the destination path on your PC
                instrument_filename = INSTR_DIR + item  # Set the SA file path
                local_file_path = os.path.join(target_directory, item)

                try:
                    # Download the file
                    data = instr.read_file_from_instrument_to_pc(instrument_filename, local_file_path)

                    # Check if data is not None before writing to the file
                    if data is not None:
                        # logging.info(f'Target Dir: {target_directory}')
                        logging.info(f'Downloading {item} to {target_directory}')
                        with open(local_file_path, 'wb') as f:
                            f.write(data)
                except Exception as e:
                    print(f"Error while downloading file '{item}': {str(e)}")

        # print('Removing files from Spectrum Analyzer')    
        instr.write(f'MMEM:DEL "{INSTR_DIR}*"')

    except Exception as e:
        logging.error(f"Error while checking instrument state: {e}")

def instrument_scanning_setup(instr):
    # Since FSV config between tabs is the same we need to reset the CF for IQ back -!! NOT TRUEE  mustfix...
    instr.write("INST:SEL 'Spectrum'")
    instr.write("SENS:SWE:WIND1:POIN 1001")
    instr.write("SENS:FREQ:CENT 1702.5MHz")
    instr.write('SENS:FREQ:SPAN 8MHz')
    instr.write("INST IQ")
    instr.write('TRAC:IQ:SRAT 6250000')
    instr.write("SENS:FREQ:CENT 1702.5MHz")

def instrument_commutation_setup(instr, center_frequency_MHz, span_MHz, points):
    try:

        instr.visa_timeout = 5000
        instr.write("INST:SEL 'Spectrum'")
        # FSV.write("CALC1:SGR:STAT OFF")
        instr.write(f"SENS:FREQ:CENT {center_frequency_MHz}MHz")
        instr.write(f"SENS:FREQ:SPAN {span_MHz}MHz")
        instr.write(f"SENS:SWE:WIND1:POIN {points}")
        instr.write(f"SENS:SWE:COUN 20")
        instr.write("INST IQ")
        instr.write(f"SENS:FREQ:CENT {center_frequency_MHz}MHz")
        instr.write("INST:SEL 'Spectrum'")

    except Exception as e:
        logging.info(f"An error occurred in instrument setup: {e}")

# def captureTrace(set_az):
def captureTrace(instr, iq, set_az, band):
    try:
        instr.write("INST:SEL 'Spectrum'")
        instr.write("INIT:IMM;*WAI")
        opc_result = instr.query('*OPC?')
        if opc_result != '1':
            logging.error(f"Operation not complete (*OPC? returned '{opc_result}')")
            return None

        trace_data = instr.query('TRAC? TRACE2')

        if iq:
            # logging.info(f'starting IQ with band: {band}')
            instr.write("INST IQ")
            if band == 'AWS1':
                instr.write('TRAC:IQ:SRAT 15360000')  # For 10MHz ABW
                # FSV.write('TRAC:IQ:SRAT 18750000')  # For 15MHz ABW
                # FSV.write('TRAC:IQ:SRAT 25000000')  # For 20MHz ABW
            elif band == 'AWS3':
                instr.write('TRAC:IQ:SRAT 6250000')  # For 5MHz ABW
            else:
                logging.error(f"Invalid band selection: {band}")
                return None

            instr.write("INIT:IMM;*WAI")  # Small delay to allow instrument to process previous commands
            opc_result_iq = instr.query('*OPC?')
            if opc_result_iq != '1':
                logging.error(f"IQ data not stored (*OPC? returned '{opc_result_iq}' after setting to IQ)")
                return None

            time_saved_IQ = f"'{set_az}'"
            instr.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")

        return trace_data

    except Exception as e:
        logging.error(f"An error occurred during captureTrace: {e}")
        return None
