import subprocess
from datetime import datetime, timedelta
import time
import logging
import requests
import os
import signal
import pandas as pd
import requests
from datetime import datetime
import json
from datetime import datetime, timezone

# Reset the Root Logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def iso_format_utc(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def analyze_results(yesterday):
    results_file_path = f"/home/noaa_gms/RFSS/toDemod/{yesterday}/results/results.csv"
    total_iq_processed = 0 

    try:
        # Read the CSV file
        df = pd.read_csv(results_file_path)

        # Count the number of 5G and LTE entries
        total_5g_count = len(df[df["5G/LTE"] == "5G"])
        total_lte_count = len(df[df["5G/LTE"] == "LTE"])
        total_iq_processed = int((total_5g_count + total_lte_count) / 20)


        # Count the number of entries where PCI is not -1 for both 5G and LTE
        pci_found_5g_count = len(df[(df["5G/LTE"] == "5G") & (df["PCI"] != -1)])
        pci_found_lte_count = len(df[(df["5G/LTE"] == "LTE") & (df["PCI"] != -1)])
        
    except FileNotFoundError:
        total_5g_count, total_lte_count = 0, 0
        pci_found_5g_count, pci_found_lte_count = 0, 0

    return df, total_iq_processed, pci_found_5g_count, pci_found_lte_count

def get_machine_id():
    with open('/etc/machine-id', 'r') as file:
        return file.read().strip()

def send_notification(df, total_iq_processed, pci_found_5g_count, pci_found_lte_count):
    machine_id = get_machine_id()

    # Notification to ntfy.sh
    ntfy_url = f'https://ntfy.sh/{machine_id}'
    ntfy_message = f"Total IQ files processed: {total_iq_processed} - 5G PCI found in: {pci_found_5g_count} files / LTE PCI found in: {pci_found_lte_count} files."
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
        if row["PCI"] != -1:  # Check if PCI is not -1
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
                "remoteID": 1003,
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
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')
    logging.info(f"IQ Processing started for {yesterday} folder")

    command = f"/home/noaa_gms/RFSS/Tools/processing/RFSS_classifyidentifyPCI_AWS1_AWS3_160ms_mat_CSV_vd8/run_RFSS_classifyidentifyPCI_AWS1_AWS3_160ms_mat_CSV_vd8.sh /usr/local/MATLAB/MATLAB_Runtime/R2023a /home/noaa_gms/RFSS/toDemod/{yesterday}/ /home/noaa_gms/RFSS/toDemod/{yesterday}/results/ '1' '0'"

    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

    # Define maximum runtime (e.g., 23 hours) - eventually this and monitor needs to be removed due to clumsiness
    max_runtime_seconds = 12 * 3600

    # Monitor the process
    for _ in range(max_runtime_seconds):
        if process.poll() is not None:
            # IQ Processing in progress...
            break
        time.sleep(1)
    else:
        # Terminate the process group
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        time.sleep(5)
        if process.poll() is None:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            logging.info("IQ process group killed.")
        else:
            logging.info("IQ process group terminated with SIGTERM.")

    # Analyze results and process
    # total_iq_processed, pci_found_5g_count, pci_found_lte_count = analyze_results(yesterday)
    df, total_iq_processed, pci_found_5g_count, pci_found_lte_count = analyze_results(yesterday)
    logging.info(f"Total IQ files processed: {total_iq_processed}, 5G PCI found in: {pci_found_5g_count} files / LTE PCI found in: {pci_found_lte_count} files.")
    # send_notification(total_iq_processed, pci_found_5g_count, pci_found_lte_count)
    send_notification(df, total_iq_processed, pci_found_5g_count, pci_found_lte_count)
    logging.info(f"IQ Processing terminated as expected.")

run_script()
