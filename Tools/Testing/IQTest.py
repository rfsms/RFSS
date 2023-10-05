import pyvisa
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.io import savemat, loadmat


# Record the start time
start_time = time.time()

# Initialize connection
RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0'
RM = pyvisa.ResourceManager()
INSTR = RM.open_resource(RESOURCE_STRING, timeout=20000)

# Clear and reset the instrument
INSTR.write("*CLS")
INSTR.write("*RST")


# Setup the analyzer for capturing I/Q data
INSTR.write(":INST:NSEL 8")
INSTR.write(":CONF:WAV")
INSTR.write(":INIT:CONT OFF")
INSTR.write('SENS:FREQ:CENT 1702500000')
INSTR.write('POW:ATT:AUTO OFF')
INSTR.write('POW:ATT 0')
INSTR.write('DISP:WAV:VIEW:NSEL 1')
INSTR.write('POW:GAIN ON')
INSTR.write('WAV:SRAT 18.75MHz')
INSTR.write('WAV:SWE:TIME 16ms')
INSTR.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
INSTR.write(":FORM:BORD SWAP")
INSTR.write(":FORM REAL,32")

# Capture and read I/Q data
INSTR.write(":INIT:IMM;*WAI")
data = INSTR.query_binary_values(":FETCH:WAV0?")

# Convert to separate I and Q arrays
i_data = data[::2]
q_data = data[1::2]

# Save I/Q data to MAT file
savemat('/home/noaa_gms/RFSS_PXA/iq_data.mat', {'I_Data': i_data, 'Q_Data': q_data})

# Close the instrument connection
INSTR.close()

# Record the end time
end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")

# Load I/Q data from MAT file
mat_data = loadmat('/home/noaa_gms/RFSS_PXA/iq_data.mat')
i_data = mat_data['I_Data'][0]
q_data = mat_data['Q_Data'][0]

# # Plotting
# plt.plot(i_data, label='I Data')
# plt.plot(q_data, label='Q Data')
# plt.xlabel('Sample')
# plt.ylabel('Value')
# plt.title('I/Q Data Line Plot')
# plt.legend()
# plt.grid(True)
# plt.show()
