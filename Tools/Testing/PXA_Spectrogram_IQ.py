import pyvisa
import time
import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import pandas as pd
from scipy.io import savemat
from PIL import Image
import subprocess

PXA_RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0::INSTR' 
RM = pyvisa.ResourceManager()
manualDir = '/home/noaa_gms/RFSS/Tools/Testing/manualCaptures'

# Specify the number of times you want to capture the trace
# The number of traces here are a direct corelation of time required for completion.
# For num_capture_iterations = 5, there will be 5 IQs transferred and one csv with 5 columns of data per waveform  
# To speed hings up you can also disable the IQ data transfer.
num_capture_iterations = 120

# Specify the center frequency in MHz, span in MHz, and number of points collected
center_frequency_mhz = 1697.5  # Center frequency in MHz
span_mhz = 6.0  # Span in MHz
num_points = 1001 # Replace with the number of points collected

# Calculate the frequency values in MHz with four decimal places
frequency_start_mhz = center_frequency_mhz - span_mhz / 2
frequency_step_mhz = span_mhz / (num_points - 1)
frequency_values_mhz = [round(frequency_start_mhz + i * frequency_step_mhz, 4) for i in range(num_points)]

# Generate a unique folder name based on current time and create the folder if it doesnt exist
folderDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
dirDate = os.path.join(manualDir, folderDate)
os.makedirs(dirDate)

# def aggregate_spectrograms(dirDate):
#     image_files = sorted(glob.glob(f"{dirDate}/*.png"), key=os.path.getmtime)
#     images = [Image.open(image_file) for image_file in image_files]

#     widths, heights = zip(*(image.size for image in images))

#     max_width = max(widths)
#     total_height = sum(heights)

#     new_image = Image.new('RGB', (max_width, total_height))

#     y_offset = 0
#     for image in images:
#         new_image.paste(image, (0, y_offset))
#         y_offset += image.height

#     new_image.save(os.path.join(dirDate, 'Aggregated_Spectrogram.png'))

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

# Function to compress and delete .mat files using subprocess
def compress_and_delete_mat_files(dirDate):
    # Store the original working directory
    original_dir = os.getcwd()

    # Check if .mat files exist
    mat_files = glob.glob(os.path.join(dirDate, "*.mat"))
    if not mat_files:
        print("No .mat files found.")
        return

    # Create a tar file
    tar_file_path = os.path.join(dirDate, f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}_mat_files.tar.gz')
    try:
        os.chdir(dirDate)
        subprocess.run(f"tar -czf {tar_file_path} *.mat", shell=True)
    finally:
        os.chdir(original_dir)  # Return to the original directory

    # Batch delete the .mat files
    for file_path in mat_files:
        os.remove(file_path)

counter = 0
data_iterations = []
timestamp_iterations = []

try:
    # Open a connection to the Spectrum Analyzer
    with RM.open_resource(PXA_RESOURCE_STRING, timeout=10000) as PXA:
        # PXA reset/setup
        PXA.write('*RST')
        PXA.write('*CLS')
        PXA.write('SYST:DEF SCR')
        pxa_idn = PXA.query('*IDN?')
        # print(f'PXA: {pxa_idn}')
        PXA.write("INIT:CONT OFF")
        PXA.write('SENS:FREQ:CENT 1697500000')
        PXA.write('FREQ:SPAN 6000000')
        PXA.write('DISP:WIND:TRAC:Y:RLEV -40')
        PXA.write('POW:ATT 0')
        PXA.write('POW:GAIN OFF')
        PXA.write('BAND:RES 1000')
        PXA.write(f'SWE:POIN {num_points}')

        PXA.write('INST:SCR:CRE;*WAI')
        PXA.write('INST:NSEL 8') # IQ Analyzer
        PXA.write('CONF:WAV')
        PXA.write('INIT:CONT OFF')
        PXA.write('SENS:FREQ:CENT 1697500000')
        PXA.write('POW:ATT:AUTO OFF')
        PXA.write('POW:ATT 0')
        PXA.write('POW:GAIN OFF')
        PXA.write('WAV:SRAT 6.25MHz')
        PXA.write('WAV:SWE:TIME 16ms')
        PXA.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
        PXA.write('FORM:BORD SWAP')
        PXA.write('FORM REAL,32')

        while True:
            # Generate a timestamp string for the current iteration
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamp_iterations.append(timestamp_str)
            print(f'Iteration: {counter}')
            
            #Swlect the spectrum Analyzer
            PXA.write('INST:SCR:SEL "Spectrum Analyzer 1"')
            # ready = PXA.query('*OPC?')
            # print(f'Ready State: {ready}')
            # PXA.write('INST:SCR:SEL "IQ Analyzer 1"')

            # Configure the instrument to fetch trace data and read/format
            PXA.write('INIT:IMM;*WAI')
            PXA.query('*OPC?')
            PXA.write(f"TRACE:DATA? TRACE1")
            trace_data = PXA.read_raw()
            trace_data = trace_data.rstrip(b'\n\r')
            # print(f'TraceData: {trace_data}')

            # Append the trace data to the list
            data_iterations.append([float(x) for x in trace_data.decode().split(',')])
            # print(f'DataIterations: {data_iterations}')
        
            # IQ Data Capture_Start
            PXA.write('INST:SCR:SEL "IQ Analyzer 1"')
            PXA.write('INIT:IMM;*WAI')
            data = PXA.query_binary_values("FETCH:WAV0?")

            # Convert to separate I and Q arrays
            i_data = data[::2]
            q_data = data[1::2]

            savemat(os.path.join(dirDate, f'{timestamp_str}.mat'), {'I_Data': i_data, 'Q_Data': q_data})
            # IQ Data Capture_End

            counter += 1

            if counter == num_capture_iterations:  
                # Create or open the CSV file for writing in append mode with timestamp in the filename
                csv_file_path = os.path.join(dirDate, f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

                # Transpose the data to create columns for each frequency point
                data_transposed = list(map(list, zip(*data_iterations)))

                with open(csv_file_path, 'a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)

                    # Write frequency data as the header row
                    header_row = ["Frequency (MHz)"] + timestamp_iterations
                    csv_writer.writerow(header_row)

                    # Write frequency and amplitude data in corresponding columns for each iteration
                    for frequency_mhz, amplitudes in zip(frequency_values_mhz, data_transposed):
                        row_to_write = [f"{frequency_mhz:.4f}"] + amplitudes
                        csv_writer.writerow(row_to_write)
                
                files_to_delete = []  # List to store .mat files to be deleted

                print("Starting tar.gz creation...")
                start_time = time.time()
                compress_and_delete_mat_files(dirDate)
                end_time = time.time()
                print(f"Tar.gz creation completed in {end_time - start_time} seconds.")

                # print(f"Trace data from {num_capture_iterations} iterations saved to {csv_file_path}")

                createSpectrogram(dirDate, timestamp_str, csv_file_path)
                print(f'Counter: {counter}')

                counter = 0
                data_iterations = []
                timestamp_iterations = []
                
            time.sleep(10)

    # After all the individual spectrograms have been generated, call the function
    # aggregate_spectrograms(dirDate)
except KeyboardInterrupt:
    print("Manually stopped by user.")