from RsInstrument import RsInstrument, RsInstrException
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

RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0'
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
FSV = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
# FSV = RsInstrument(RESOURCE_STRING, False, False, 'simulate=True')
INSTR_DIR = 'c:\\R_S\\Instr\\user\\RFSS\\'

def check_instrument_state():
    try:
        # Check the instrument's event status register to ensure no errors
        sesr = FSV.query("*ESR?")
        logging.info(f"Instrument SESR: {sesr}")

        # Check if the operation is complete
        opc = FSV.query("*OPC?")
        logging.info(f"Instrument Operation Complete: {opc}")
        
        # Check the status byte register
        stb = FSV.query("*STB?")
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

def get_SpecAn_content_and_DL_locally(target_directory):
    try:

        check_instrument_state()

        # Set and list the current directory on the SA
        FSV.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = FSV.query('MMEM:CAT?')
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
                    data = FSV.read_file_from_instrument_to_pc(instrument_filename, local_file_path)

                    # Check if data is not None before writing to the file
                    if data is not None:
                        # logging.info(f'Target Dir: {target_directory}')
                        logging.info(f'Downloading {item} to {target_directory}')
                        with open(local_file_path, 'wb') as f:
                            f.write(data)
                except Exception as e:
                    print(f"Error while downloading file '{item}': {str(e)}")

        # print('Removing files from Spectrum Analyzer')    
        FSV.write(f'MMEM:DEL "{INSTR_DIR}*"')

    except RsInstrException as e:
        if "-256," in str(e):
            logging.warning("No files on Spectrum Analyzer to process:", e)
        else:
            logging.error(f"Error in get_SpecAn_content_and_DL_locally: {e}")

def instrument_scanning_setup():
    # Since FSV config between tabs is the same we need to reset the CF for IQ back -!! NOT TRUEE  mustfix...
    FSV.write("INST:SEL 'Spectrum'")
    FSV.write("SENS:SWE:WIND1:POIN 1001")
    FSV.write("SENS:FREQ:CENT 1702.5MHz")
    FSV.write('SENS:FREQ:SPAN 8MHz')
    FSV.write("INST IQ")
    FSV.write('TRAC:IQ:SRAT 6250000')
    FSV.write("SENS:FREQ:CENT 1702.5MHz")

def instrument_commutation_setup(center_frequency_MHz, span_MHz, points):
    try:

        FSV.visa_timeout = 5000
        FSV.write("INST:SEL 'Spectrum'")
        # FSV.write("CALC1:SGR:STAT OFF")
        FSV.write(f"SENS:FREQ:CENT {center_frequency_MHz}MHz")
        FSV.write(f"SENS:FREQ:SPAN {span_MHz}MHz")
        FSV.write(f"SENS:SWE:WIND1:POIN {points}")
        FSV.write(f"SENS:SWE:COUN 20")
        FSV.write("INST IQ")
        FSV.write(f"SENS:FREQ:CENT {center_frequency_MHz}MHz")
        FSV.write("INST:SEL 'Spectrum'")

    except KeyboardInterrupt:
        print(f"An error occurred in instrument setup")

# def captureTrace(set_az):
def captureTrace(iq, set_az, band):
    try:
        FSV.write("INST:SEL 'Spectrum'")
        FSV.write("INIT:IMM")
        opc_result = FSV.query('*OPC?')
        if opc_result != '1':
            logging.error(f"Operation not complete (*OPC? returned '{opc_result}')")
            return None

        trace_data = FSV.query('TRAC? TRACE2')

        if iq:
            # logging.info(f'starting IQ with band: {band}')
            FSV.write("INST IQ")
            if band == 'AWS1':
                FSV.write('TRAC:IQ:SRAT 12500000')  # For 10Mhz ABW
            elif band == 'AWS3':
                FSV.write('TRAC:IQ:SRAT 6250000')  # For 5Mhz ABW
            else:
                logging.error(f"Invalid band selection: {band}")
                return None

            FSV.write("INIT:IMM")  # Small delay to allow instrument to process previous commands
            opc_result_iq = FSV.query('*OPC?')
            if opc_result_iq != '1':
                logging.error(f"IQ data not stored (*OPC? returned '{opc_result_iq}' after setting to IQ)")
                return None

            time_saved_IQ = f"'{set_az}'"
            FSV.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")

        return trace_data

    except Exception as e:
        logging.error(f"An error occurred during captureTrace: {e}")
        return None
