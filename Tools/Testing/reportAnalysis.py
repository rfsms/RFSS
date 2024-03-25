import os
import subprocess
from prettytable import PrettyTable

root_dir = "/home/noaa_gms/RFSS/toDemod/"

def count_mat_files(directory):
    # Function to find all files in directory matching *.mat and return total number of hits
    command = f'find "{directory}" -maxdepth 1 -name "*.mat" | wc -l'
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return "0"

def grep_count(file, pattern):
    # Function to perform a grep on 'pattern' parameter in working results file and return number of hits
    # Pattern could be 'DROPPED' or '5G,-1' 
    try:
        command = f'grep -io "{pattern}" "{file}" | wc -l'
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return "0"

def grep_v_count(file, pattern):
    #Function to inverse grep for 'pattern' parameter from working results file and then
    # return a count of all of those with ',5G,'
    try:
        command = f'grep -v "{pattern}" "{file}" | grep -c ",5G,"'
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return "0"

def pci_counts(file):
    # Function to first perform an inverse grep fo '5G,-1' from working results file
    # and then awk the results for PCIs, then finally strip duplicates in a row and return the unique PCIs
    try:
        command = f'grep -v "5G,-1" "{file}" | awk -F, \'$3 ~ /^[0-9]+$/ {{print $3}}\' | sort | uniq -c'
        pci_count_output = subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        pci_count_output = ""
    pci_counts = {}
    for line in pci_count_output.split('\n'):
        if line.strip():
            count, pci = line.strip().split(maxsplit=1)
            pci_counts[pci] = count
    return pci_counts

# Initialize PrettyTable
table = PrettyTable()
table.field_names = ["Directory", "Subdirectory", "Unprocessed MAT files", "Total Dropped IQ", "Processed IQ", "Valid PCI entries", "PCI counts"]

for upper_dir in sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]):
    upper_dir_path = os.path.join(root_dir, upper_dir)
    for dirpath, dirnames, filenames in os.walk(upper_dir_path):
        # Skip the "results" directories
        dirnames[:] = [d for d in dirnames if d != "results"]
        for dirname in sorted(dirnames):
            dir_full_path = os.path.join(dirpath, dirname)
            results_file = os.path.join(dir_full_path, "results/results.csv")
            mat_files = count_mat_files(dir_full_path)
            if os.path.isfile(results_file):
                row = [upper_dir, dirname, mat_files, "N/A", "N/A", "N/A", "Results file does not exist"]
                dropped_count = grep_count(results_file, 'DROPPED')
                non_classify_identify = grep_count(results_file, '5G,-1')
                valid_pci_count = grep_v_count(results_file, '5G,-1')
                if dropped_count != "0" or non_classify_identify != "0" or valid_pci_count != "0":
                    pci_counts_output = pci_counts(results_file)
                    pci_counts_str = "\n".join([f"PCI {pci}: {count}" for pci, count in pci_counts_output.items()])
                    row = [upper_dir, dirname, mat_files, dropped_count, non_classify_identify, valid_pci_count, pci_counts_str]
                table.add_row(row)
print(table)
