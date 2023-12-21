import subprocess
from datetime import datetime, timedelta
import time
import logging
import requests
import os
import signal
import pandas as pd

# Reset the Root Logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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


    # print(f"Total 5G: {total_5g_count}, Total LTE: {total_lte_count}")
    return total_iq_processed, pci_found_5g_count, pci_found_lte_count
    # print(f"PCI found in 5G: {pci_found_5g_count}, PCI found in LTE: {pci_found_lte_count}")

def get_machine_id():
    with open('/etc/machine-id', 'r') as file:
        return file.read().strip()
    
def send_notification(total_iq_processed, pci_found_5g_count, pci_found_lte_count):
    machine_id = get_machine_id()
    url = f'https://ntfy.sh/{machine_id}'
    message = f"Total IQ files processed: {total_iq_processed} - 5G PCI found in: {pci_found_5g_count} files / LTE PCI found in: {pci_found_lte_count} files."
    data = {'IQ Analysis': message}
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while sending notification: {e}")
    return None

def run_script():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')
    logging.info(f"IQ Processing started for {yesterday} folder")

    command = f"/home/noaa_gms/RFSS/Tools/processing/RFSS_classifyidentifyPCI_AWS1_AWS3_160ms_mat_CSV_vd8/run_RFSS_classifyidentifyPCI_AWS1_AWS3_160ms_mat_CSV_vd8.sh /usr/local/MATLAB/MATLAB_Runtime/R2023a /home/noaa_gms/RFSS/toDemod/{yesterday}/ /home/noaa_gms/RFSS/toDemod/{yesterday}/results/ '1' '0'"

    process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

    # Define maximum runtime (e.g., 23 hours)
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

    # Analyze results
    total_iq_processed, pci_found_5g_count, pci_found_lte_count = analyze_results(yesterday)
    logging.info(f"Total IQ files processed: {total_iq_processed}, 5G PCI found in: {pci_found_5g_count} files / LTE PCI found in: {pci_found_lte_count} files.")
    send_notification(total_iq_processed, pci_found_5g_count, pci_found_lte_count)
    logging.info(f"IQ Processing terminated as expected.")

run_script()
