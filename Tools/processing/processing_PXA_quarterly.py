import subprocess
from datetime import datetime, timedelta, timezone
import logging
import requests
import os
import pandas as pd
import requests
import json
import glob

# Read vals from the config.json file
config_file_path = '/home/noaa_gms/RFSS/Tools/config.json'
with open(config_file_path, 'r') as json_file:
    config_data = json.load(json_file)

# Read vars from /home/noaa_gms/RFSS/Tools/config.json
location = config_data['location']
remoteID = config_data['remoteID']
snrThreshold = config_data['snrThreshold']
numSnapshots = config_data['numSnapshots']

# Reset the Root Logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def iso_format_utc(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def analyze_results(daily_folder, quarter_folder):
    results_file_path = f"/home/noaa_gms/RFSS/toDemod/{daily_folder}/{quarter_folder}/results/results.csv"
   
    total_mat_processed = 0 
    total_dropped = 0

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    try:
        if os.path.exists(results_file_path):
            logging.info(f"Confirmed existence of results file at {results_file_path}")
        else:
            logging.info(f"Results file not found at {results_file_path} before reading")

        # Read the CSV file
        df = pd.read_csv(results_file_path)

        # Extract unique timestamp prefixes
        unique_timestamp_prefixes = df['timestamp'].str.extract(r'(\d{8}_\d{6})')[0].unique()

         # Count the number of unique timestamp prefixes
        total_mat_processed = len(unique_timestamp_prefixes)

        # Count the number of entries where PCI is not -1 for both 5G and LTE
        pci_found_5g_count = len(df[(df["5G/LTE"] == "5G") & (df["PCI"] != -1)])
        pci_found_lte_count = len(df[(df["5G/LTE"] == "LTE") & (df["PCI"] != -1)])

        # Count the number of 'DROPPED' entries
        total_dropped = len(df[df["Processed/NotProcessed"] == "DROPPED"])
        
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError for {results_file_path}: {str(e)}")
        # Lets initialize vars to a default state om the even of an error and not cause the script to crash 
        pci_found_5g_count, pci_found_lte_count, total_dropped = 0, 0, 0

    return df, total_mat_processed, pci_found_5g_count, pci_found_lte_count, total_dropped

def get_machine_id():
    with open('/etc/machine-id', 'r') as file:
        return file.read().strip()

def send_notification(df, total_mat_processed, pci_found_5g_count, pci_found_lte_count, total_dropped):
    machine_id = get_machine_id()

    # Notification to ntfy.sh
    ntfy_url = f'https://ntfy.sh/{machine_id}'
    ntfy_message = f"Total MAT files captured: {total_mat_processed}, 5G PCI found in: {pci_found_5g_count} files / LTE PCI found in: {pci_found_lte_count} files, Total Dropped IQ files: {total_dropped}."
    ntfy_data = {'IQ Analysis': ntfy_message}

    try:
        ntfy_response = requests.post(ntfy_url, json=ntfy_data)
        ntfy_response.raise_for_status()
        logging.info("Notification sent to ntfy.sh successfully.")
    except requests.exceptions.RequestException as e:
        logging.info("Error occurred while sending notification to ntfy.sh:", str(e))

    # Transform DataFrame into the specified JSON structure for the API POST
    events = []
    for _, row in df.iterrows():
        # Create an event only if the PCI value is valid (not NaN, not -1), 
        # the signal type (5G/LTE) is specified and not NaN, 
        # and the power level (SNR(dB)) is available
        if pd.notna(row["PCI"]) and row["PCI"] != -1 and pd.notna(row["5G/LTE"]):
            event = {
                "PCI": row["PCI"],
                "_id": 0,
                "beam": "upper hemisphere scanning",
                "carrierID": "Unknown",
                "cellID": "Unknown",
                "eNodeB": "Unknown",
                "elevationAngle": 0,
                "elevationAngleUnits": "degrees",
                "eventID": row["timestamp"],
                "headingAzimuth": 0,
                "headingAzimuthUnits": "degrees",
                "inverseAxialRatio": 0,
                "labels": "None",
                "locationLat": 0,
                "locationLatUnits": "degrees",
                "locationLon": 0,
                "locationLonUnits": "degrees",
                "maxBandwidth": 0,
                "maxBandwidthUnits": "kHz",
                "maxFrequency": 0,
                "maxFrequencyUnits": "MHz",
                "maxPower": row["SNR(dB)"] if row["SNR(dB)"] != "" else 0,
                "maxPowerUnits": "dBm",
                "mode": "Operational",
                "notifyCarrier": None,
                "remoteID": {remoteID},
                "severityLevel": "warning",
                "signalType": row["5G/LTE"],
                "tiltAngle": 0,
                "tiltAngleUnits": "degrees",
                "timestamp": iso_format_utc(datetime.now())
            }
            
            events.append(event)

    # Prepare data for API POST request
    api_url = "https://ec2-52-61-173-155.us-gov-west-1.compute.amazonaws.com/api/data"
    api_data = {'events': events}

    logging.info("Sending the following data to API: %s", json.dumps(api_data, indent=4))

    # Send POST request to API
    try:
        api_response = requests.post(api_url, json=api_data, verify=False)
        logging.info("Request sent to API successfully.")

        if api_response.status_code == 200:
            logging.info("API Response: %s", api_response.text)
        else:
            logging.info("Eresponse from API server: %s", api_response.text)
    except requests.exceptions.RequestException as e:
        logging.error("An error occurred during the API request: %s", str(e))

def run_script():
    last_hour = datetime.utcnow() - timedelta(hours=1)
    daily_folder = last_hour.strftime('%Y_%m_%d')

    # Determine the quarter of the day
    hour = last_hour.hour
    if hour < 6:
        quarter_folder = '0000-0559'
    elif hour < 12:
        quarter_folder = '0600-1159'
    elif hour < 18:
        quarter_folder = '1200-1759'
    else:
        quarter_folder = '1800-2359'

    mat_files_path = f"/home/noaa_gms/RFSS/toDemod/{daily_folder}/{quarter_folder}/*.mat"

    # Log the path being checked
    logging.info(f"Checking for .mat files in: {mat_files_path}")

    # Check if there are .mat files in the last hour's folder
    mat_files = glob.glob(mat_files_path)

    if not mat_files:
        logging.info(f"No .mat files found in {quarter_folder}, skipping processing.")
        return

    # Set up the results folder for today
    results_folder_path = f"/home/noaa_gms/RFSS/toDemod/{daily_folder}/{quarter_folder}/results"
    os.makedirs(results_folder_path, exist_ok=True)

    logging.info(f"IQ Processing started for {quarter_folder} folder")

    command = f"/home/noaa_gms/RFSS/Tools/processing/RFSS_classifyidentify_AWS1_AWS3_160ms_thresholdSNR116_vd12/run_RFSS_classifyidentify_AWS1_AWS3_160ms_thresholdSNR116_vd12.sh /usr/local/MATLAB/MATLAB_Runtime/R2023a /home/noaa_gms/RFSS/toDemod/{daily_folder}/{quarter_folder} /home/noaa_gms/RFSS/toDemod/{daily_folder}/{quarter_folder}/results '1' '0' '{snrThreshold}' '{location}' '{numSnapshots}'"
    logging.info(f"Starting MATLAB process with: {command}")
    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

    # Wait to coomplete the process
    process.wait()
    logging.info("MATLAB process completed.")

    # NOW...Analyze results and report
    df, total_mat_processed, pci_found_5g_count, pci_found_lte_count, total_dropped = analyze_results(daily_folder, quarter_folder)
    logging.info(f"Total MAT files captured: {total_mat_processed}, Number of IQ snapshots extracted per MAT File:: {numSnapshots}, Total IQs extracted: {total_mat_processed*numSnapshots}, 5G PCI found in: {pci_found_5g_count} files / LTE PCI found in: {pci_found_lte_count} files, Total Dropped IQ files: {total_dropped}.")

    send_notification(df, total_mat_processed, pci_found_5g_count, pci_found_lte_count, total_dropped)
    logging.info(f"IQ Processing terminated as expected.")

run_script()
