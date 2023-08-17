import os
import glob
import subprocess

def scp_gz_files_and_delete(source_dir, remote_ip, remote_username, remote_path):
    try:
        # List all tar.gz files in the source directory
        file_list = glob.glob(os.path.join(source_dir, '*tar.gz'))

        if not file_list:
            print("No *.tar.gz files found in the source directory.")
            return

        # Construct the scp command
        scp_cmd = [
            'scp',
            '-r',  # Use -r for recursively copying directories
            *file_list,
            f'{remote_username}@{remote_ip}:{remote_path}'
        ]

        # Run the scp command using subprocess and capture stdout and stderr
        process = subprocess.Popen(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Process and print the progress
        for line in process.stderr:
            if line.startswith('Sending'):
                print(line.strip())

        # Wait for the process to complete
        process.wait()

        print("All .gz files successfully copied to the remote server.")

        # Delete the files from the source directory
        for file_path in file_list:
            os.remove(file_path)

        print("All .gz files deleted from the source directory.")
    except subprocess.CalledProcessError as e:
        print("Error while copying files:", e)


# SCP Setup
source_directory = "/home/noaa_gms/RFSS/Received"
remote_ip = "noaa-gms-ec2"
remote_username = "Administrator"
remote_path = "/"

scp_gz_files_and_delete(source_directory, remote_ip, remote_username, remote_path)