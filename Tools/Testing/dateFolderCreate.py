import os
import shutil
import re

# Directory containing the files
directory = "/home/noaa_gms/RFSS/toDemod/2024_01_03"

# Regex pattern to extract date and hour from filename
pattern = r"(\d{8})_(\d{2})\d{4}_UTC_.*"

for filename in os.listdir(directory):
    match = re.match(pattern, filename)
    if match:
        date, hour = match.groups()
        # Create a folder name based on the date and hour
        hour_folder = os.path.join(directory, f"{date}_{hour}00_UTC")
        # Create the hour-specific folder if it doesn't exist
        if not os.path.exists(hour_folder):
            os.makedirs(hour_folder)
        
        # Create a 'results' subfolder inside the hour folder
        results_folder = os.path.join(hour_folder, "results")
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        # Move the file to the corresponding hour folder
        shutil.move(os.path.join(directory, filename), hour_folder)
