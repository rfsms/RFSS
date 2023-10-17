# Only communicates with SA (PXA) to capture a single trace and then repeats for 'num_capture_iterations'
# Then creates a spectrogram on the resulting data. 

import pyvisa
import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np


# Initialize the VISA resource manager
RM = pyvisa.ResourceManager()

PXA_RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0'

# Specify the number of times you want to capture the trace
num_capture_iterations = 100

# Initialize a list to store data from each iteration and timestamps
data_iterations = []
timestamp_iterations = []

# Open a connection to the Spectrum Analyzer
with RM.open_resource(PXA_RESOURCE_STRING) as PXA:
    for iteration in range(num_capture_iterations):
        # Generate a timestamp string for the current iteration
        timestamp_str = datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")
        timestamp_iterations.append(timestamp_str)
        print(f'Iteration: {iteration}')
        
        # Configure the instrument to fetch trace data
        PXA.write('INIT:IMM;*WAI')
        PXA.write(f"TRACE:DATA? TRACE1")

        # Read the amplitude data from the instrument
        trace_data = PXA.read_raw()

        # Remove trailing newline or carriage return characters
        trace_data = trace_data.rstrip(b'\n\r')

        # Append the trace data to the list
        data_iterations.append(trace_data.decode().split(','))

# Specify the center frequency in MHz, span in MHz, and number of points collected
center_frequency_mhz = 1702.5  # Center frequency in MHz
span_mhz = 20.0  # Span in MHz
num_points = 1000  # Replace with the number of points collected

# Calculate the frequency values in MHz with four decimal places
frequency_start_mhz = center_frequency_mhz - span_mhz / 2
frequency_step_mhz = span_mhz / (num_points - 1)
frequency_values_mhz = [round(frequency_start_mhz + i * frequency_step_mhz, 4) for i in range(num_points)]

# Transpose the data to create columns for each frequency point
data_transposed = list(map(list, zip(*data_iterations)))

# Create or open the CSV file for writing in append mode with timestamp in the filename
csv_file_path = f'spectrum_trace_with_frequency_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
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

# Convert the frequency values and amplitude data to numpy arrays for plotting
frequency_values_mhz = np.array(frequency_values_mhz)
data_iterations = np.array(data_iterations).astype(float)

# Plot the rotated spectrogram
plt.figure(figsize=(10, 6))
plt.imshow(data_iterations, aspect='auto', cmap='inferno', origin='lower',
           extent=[frequency_values_mhz[0], frequency_values_mhz[-1], 0, num_capture_iterations-1])

plt.colorbar(label='Amplitude (dB)')
plt.yticks(range(num_capture_iterations), timestamp_iterations)  # Set yticks as timestamps
plt.xlabel('Frequency (MHz)')
plt.title('Rotated Spectrogram with Timestamps')

# Save the plot
plt.savefig(f'spectrogram_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png')

plt.show()