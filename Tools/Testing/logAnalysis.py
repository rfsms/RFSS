import pandas as pd
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio

# Function to parse the timestamp and return satellite, start time, and end time
def parse_timestamp(timestamp):
    pattern = r'(\d{8}_\d{6})_UTC_(.*?)_AZ_(\d+)_EL_(\d+).mat_(\d+)'
    match = re.match(pattern, timestamp)
    if match:
        return match.group(2), match.group(1)
    return None, None

# Function to determine if the row represents a processed file
def is_processed(row):
    return row['5G/LTE'] == 'LTE' and row['PCI'] == -1

# Load the uploaded CSV file
file_path = '/home/noaa_gms/RFSS/toDemod/2024_01_22/0000-0559/results/results.csv'
data = pd.read_csv(file_path)

# Analyzing the data
data_summary = defaultdict(lambda: {'PROCESSED': 0, 'DROPPED': 0, 'start_time': '', 'end_time': ''})

for index, row in data.iterrows():
    satellite, timestamp = parse_timestamp(row['timestamp'])
    if satellite:
        # Update start and end time
        if data_summary[satellite]['start_time'] == '' or timestamp < data_summary[satellite]['start_time']:
            data_summary[satellite]['start_time'] = timestamp
        if data_summary[satellite]['end_time'] == '' or timestamp > data_summary[satellite]['end_time']:
            data_summary[satellite]['end_time'] = timestamp

        # Count processed and dropped
        if is_processed(row):
            data_summary[satellite]['PROCESSED'] += 1
        elif row['Processed/NotProcessed'] == 'DROPPED':
            data_summary[satellite]['DROPPED'] += 1

# Converting summary to a more readable format
summary_data = []
for satellite, info in data_summary.items():
    summary_data.append({
        'Satellite': satellite,
        'Start Time': info['start_time'],
        'End Time': info['end_time'],
        'Processed': info['PROCESSED'],
        'Dropped': info['DROPPED']
    })

# Convert summary to DataFrame for better visualization
summary_df = pd.DataFrame(summary_data)
summary_df.sort_values(by=['Satellite', 'Start Time'], inplace=True)
print(summary_df)

# Grouping data by satellite and elevation, and counting processed and dropped passes
# Initialize a dictionary to hold the data
elevation_summary = defaultdict(lambda: defaultdict(lambda: {'PROCESSED': 0, 'DROPPED': 0}))

for index, row in data.iterrows():
    satellite, _ = parse_timestamp(row['timestamp'])
    if satellite:
        elevation = int(re.search(r'EL_(\d+)', row['timestamp']).group(1))
        # Count processed and dropped based on elevation
        if is_processed(row):
            elevation_summary[satellite][elevation]['PROCESSED'] += 1
        elif row['Processed/NotProcessed'] == 'DROPPED':
            elevation_summary[satellite][elevation]['DROPPED'] += 1

# Converting elevation summary to a DataFrame
elevation_data = []
for satellite, elevations in elevation_summary.items():
    for elevation, counts in elevations.items():
        elevation_data.append({
            'Satellite': satellite,
            'Elevation': elevation,
            'Processed': counts['PROCESSED'],
            'Dropped': counts['DROPPED']
        })

elevation_df = pd.DataFrame(elevation_data)

# Sort the dataframe for better visualization
elevation_df.sort_values(by=['Satellite', 'Elevation'], inplace=True)

print(elevation_df)  # Display the first few rows of the elevation dataframe




# Plotting elevation vs. processed/dropped for each satellite
plt.figure(figsize=(12, 8))

# Predefined colors for each satellite
colors = {'METOP-B': 'orange', 'METOP-C': 'blue', 'NOAA-19': 'green', 'NOAA-18': 'red'}


for satellite in elevation_summary.keys():
    elevations = []
    processed = []
    dropped = []
    
    for elevation, counts in elevation_summary[satellite].items():
        elevations.append(elevation)
        processed.append(counts['PROCESSED'])
        dropped.append(counts['DROPPED'])

    # Assigning color based on the satellite
    color = colors.get(satellite, 'black')  # Default to black if satellite not in predefined list

    # Plotting
    plt.plot(elevations, processed, marker='o', color=color, linestyle='-', label=f'{satellite} - Processed')
    plt.plot(elevations, dropped, marker='x', color=color, linestyle='--', label=f'{satellite} - Dropped')

plt.xlabel('Elevation')
plt.ylabel('Count')
plt.title('Processed vs Dropped Counts by Elevation for Each Satellite')
plt.legend()
plt.grid(True)

# Setting x-axis limits and ticks
plt.xlim(0, 180)
plt.xticks(range(0, 181, 10), rotation=45)  # Adjust the step size as needed

# Saving the plot to a PNG file
plot_path = 'satellite_elevation_analysis.png'
plt.savefig(plot_path)

plt.show()

plot_path