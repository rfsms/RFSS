import json

# Path to the JSON configuration file
config_file_path = '/home/noaa_gms/RFSS/Tools/Testing/config.json'

# Reading the data from the JSON file
with open(config_file_path, 'r') as json_file:
    config_data = json.load(json_file)

# Printing the configuration data
for key, value in config_data.items():
    print(f"{key}: {value}")
