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


PXA_RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0::INSTR' 
MXG_RESOURCE_STRING = 'TCPIP::192.168.130.66::5025::SOCKET' 
RM = pyvisa.ResourceManager()

manualDir = '/home/noaa_gms/RFSS/Tools/Testing/manualCaptures'

# Specify the number of times you want to capture the trace
num_capture_iterations = 2

# Specify the center frequency in MHz, span in MHz, and number of points collected
center_frequency_mhz = 1702.5  # Center frequency in MHz
span_mhz = 20.0  # Span in MHz
num_points = 1000 # Replace with the number of points collected

# Calculate the frequency values in MHz with four decimal places
frequency_start_mhz = center_frequency_mhz - span_mhz / 2
frequency_step_mhz = span_mhz / (num_points - 1)
frequency_values_mhz = [round(frequency_start_mhz + i * frequency_step_mhz, 4) for i in range(num_points)]

# Generate a unique folder name based on current time
folderDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
dirDate = os.path.join(manualDir, folderDate)

# Create the new directory
os.makedirs(dirDate)

waveforms_15MHz = [
"2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK.ARB",
# "2-1-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_1PRB_GUARDBAND.ARB",
# "2-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_2PRB_GUARDBAND.ARB",
# "2-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_3PRB_GUARDBAND.ARB",
# "4-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1698_QPSK.ARB",
# "6-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1702_QPSK.ARB",
# "6-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1702_QPSK_2PRB_GUARDBAND.ARB",
# "6-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1702_QPSK_3PRB_GUARDBAND.ARB",
# "7-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1702_QPSK.ARB",
# "8-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK.ARB",
# "8-1-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK_1PRB_GUARDBAND.ARB",
# "8-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK_2PRB_GUARDBAND.ARB",
# "8-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK_3PRB_GUARDBAND.ARB",
# "9-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1707_QPSK.ARB",
# "16-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_QPSK_METOP.ARB",
# "16-1-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_1PRB_GUARDBAND.ARB",
# "16-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_2PRB_GUARDBAND.ARB",
# "16-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_3PRB_GUARDBAND.ARB",
# "17-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB",
# "18-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_PUCCH.ARB",
# "19-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_QPSK_METOP_PUCCH.ARB",
# "22-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_NONBLANKED.ARB",
# "23-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_NONBLANKED.ARB"
]

# waveforms_5MHz = [
# "1-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK.ARB"
# "1-1-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_1PRB_GUARDBAND.ARB"
# "1-2-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_2PRB_GUARDBAND.ARB"
# "1-3-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_3PRB_GUARDBAND.ARB"
# "3-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLDFT_ALLPUSCH_1698_QPSK.ARB"
# "5-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH1_PRBSET11TO24_5MHZ_VAR_1698.ARB"
# "10-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_QPSK_METOP.ARB"
# "10-1-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_1PRB_GUARDBAND.ARB"
# "10-2-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_2PRB_GUARDBAND.ARB"
# "10-3-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_3PRB_GUARDBAND.ARB"
# "11-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB"
# "12-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH14_PRBSET24_5MHZ_VAR_1701_METOP.ARB"
# "13-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH14_PRBSET23TO24_5MHZ_VAR_1701_METOP.ARB"
# "14-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH14_PRBSET24_INTERASLOTHOPPING_5MHZ_VAR_1701_METOP.ARB"
# "15-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH1_PRBSET11TO24_5MHZ_VAR_1701_METOP.ARB"
# "20-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_QPSK_NONBLANKED.ARB"
# "21-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLDFT_ALLPUSCH_QPSK_NONBLANKED.ARB"
# ]

def createSpectrogram(dirDate):
    # Collect all the CSV files generated
    csv_files = glob.glob(f"{dirDate}/*.csv")

    # Initialize empty lists to collect all data and timestamps
    all_data = []
    all_timestamps = []
    
    # Loop through each CSV file to read its content
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        frequencies = df['Frequency (MHz)']
        timestamps = df.columns[1:]
        data = df.iloc[:, 1:].to_numpy()
        
        all_data.append(data)
        all_timestamps.extend(timestamps)

    # Convert the list of arrays into a single 2D NumPy array
    all_data = np.concatenate(all_data, axis=1)
    all_data = all_data.T  # Transpose the data array
    all_timestamps = np.array(all_timestamps)

    # Plot the rotated spectrogram
    plt.figure(figsize=(10, 6))
    plt.imshow(all_data, aspect='auto', cmap='viridis', origin='lower',
            extent=[frequencies.iloc[0], frequencies.iloc[-1], 0, len(all_timestamps)-1])

    plt.colorbar(label='Amplitude (dB)')
    plt.yticks(range(len(all_timestamps)), all_timestamps)
    plt.xlabel('Frequency (MHz)')
    plt.title(f'Aggregated_Spectrogram\n{timestamp_str} UTC')

    # Save the plot
    plt.savefig(os.path.join(dirDate, f'Aggregated_Spectrogram_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'))

    # plt.show()

# Open a connection to the Spectrum Analyzer
with RM.open_resource(PXA_RESOURCE_STRING) as PXA:
    # PXA reset/setup
    PXA.write('*RST')
    PXA.write('*CLS')
    PXA.write('SYST:DEF SCR')
    pxa_idn = PXA.query('*IDN?')
    print(f'PXA: {pxa_idn}')
    PXA.write("INIT:CONT ON")
    PXA.write('SENS:FREQ:CENT 1702500000')
    PXA.write('FREQ:SPAN 20000000')
    PXA.write('DISP:WIND:TRAC:Y:RLEV -40')
    PXA.write('POW:ATT 0')
    PXA.write('POW:GAIN ON')
    PXA.write('BAND:RES 1000')
    PXA.write(f'SWE:POIN {num_points}')

    PXA.write('INST:SCR:CRE')
    PXA.write('INST:NSEL 8') # IQ Analyzer
    PXA.write('CONF:WAV')
    PXA.write('INIT:CONT OFF')
    PXA.write('SENS:FREQ:CENT 1702500000')
    PXA.write('POW:ATT:AUTO OFF')
    PXA.write('POW:ATT 0')
    PXA.write('POW:GAIN ON')
    PXA.write('WAV:SRAT 18.75MHz')
    PXA.write('WAV:SWE:TIME 16ms')
    PXA.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
    PXA.write('FORM:BORD SWAP')
    PXA.write('FORM REAL,32')

with RM.open_resource(MXG_RESOURCE_STRING, timeout=2000) as MXG:
    MXG.read_termination = '\n'
    MXG.write_termination = '\n'
    
    # MXG reset/setup
    MXG.write('*IDN?')
    mxg_idn = MXG.read()
    print(f'MXG: {mxg_idn}')

    #RMXG Config
    MXG.write('*RST')
    MXG.write('*CLS')

    MXG.write(':FREQ 1702.5 MHZ')
    freq = MXG.query_ascii_values(':FREQ?')
    # print(f'CF: {freq}')

    MXG.write(':POW -60 DBM')
    power = MXG.query_ascii_values(':POW?')
    # print(f'Power: {power}')

    # Extract waveform names from the response
    for entry in waveforms_15MHz:
        # print(f'setting up now and sending "{entry}"')

        MXG.write(f':RAD:ARB:WAV "{entry}"')
        # MXG.write(':RAD:ARB:WAV "%s"' % ('17-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB'))
        # MXG.write('RAD:ARB:WAV "17-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB"')
        waveform = MXG.query(':RAD:ARB:WAV?')
        waveform_clean = waveform.replace('"', '')
        print(f'WFM Configured: {waveform}')

        MXG.write(':RAD:ARB:SCL:RATE 23.04 MHZ')
        sampleClock = MXG.query_ascii_values(':RAD:ARB:SCL:RATE?')
        # print(f'Sample Clock: {sampleClock}')

        if MXG.query('*OPC?') == '1':
            MXG.write(':RAD:ARB 1')
            MXG.write(':OUTP 1')
            time.sleep(2)

            with RM.open_resource(PXA_RESOURCE_STRING, timeout = 2000) as PXA:
                # Initialize a list to store data from each iteration and timestamps
                data_iterations = []
                timestamp_iterations = []
                for iteration in range(num_capture_iterations):
                    # Generate a timestamp string for the current iteration
                    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    timestamp_iterations.append(timestamp_str)
                    print(f'Iteration: {iteration}')
                    
                    #Swlect the spectrum Analyzer
                    PXA.write('INST:SCR:SEL "Spectrum Analyzer 1"')
                    ready = PXA.query('*OPC?')
                    print(f'Ready State: {ready}')
                    # PXA.write('INST:SCR:SEL "IQ Analyzer 1"')

                    # Configure the instrument to fetch trace data and read/format
                    PXA.write('INIT:IMM;*WAI')
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
                    data = PXA.query_binary_values(":FETCH:WAV0?")

                    # Convert to separate I and Q arrays
                    i_data = data[::2]
                    q_data = data[1::2]

                    savemat(os.path.join(dirDate, f'{waveform_clean}_{timestamp_str}.mat'), {'I_Data': i_data, 'Q_Data': q_data})
                    # IQ Data Capture_End
                     
            # Create or open the CSV file for writing in append mode with timestamp in the filename
            csv_file_path = os.path.join(dirDate, f'{waveform_clean}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            
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
            
            print(f"Trace data from {num_capture_iterations} iterations saved to {csv_file_path}")

            # # Setup the plots by converting the frequency values and amplitude data 
            # # to numpy arrays for plotting
            # frequency_values_mhz = np.array(frequency_values_mhz)
            # np_data_iterations = np.array(data_iterations).astype(float)

            # # Plot the spectrogram
            # plt.figure(figsize=(10, 6))
            # # plt.imshow(data_iterations, aspect='auto', cmap='inferno', origin='lower', 
            # #            extent=[frequency_values_mhz[0], frequency_values_mhz[-1], 0, num_capture_iterations-1])

            # plt.imshow(data_iterations, aspect='auto', cmap='viridis', origin='lower', 
            #            extent=[frequency_values_mhz[0], frequency_values_mhz[-1], 0, num_capture_iterations-1])

            # plt.colorbar(label='Amplitude (dB)')
            # plt.yticks(range(len(timestamp_iterations)), timestamp_iterations)
            # plt.xlabel('Frequency (MHz)')
            # plt.title(f'{waveform_clean}\n{timestamp_str}')

            # # Save the plot
            # plt.savefig(os.path.join(dirDate, f'spectrogram_{waveform_clean}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'))

            # plt.show()

        else:
            print("Operation issue")
            break     

createSpectrogram(dirDate)
       
