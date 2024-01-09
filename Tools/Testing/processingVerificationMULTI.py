import subprocess
import concurrent.futures
import time
import psutil

# Function to get current memory and swap usage
def get_memory_usage():
    memory_usage = psutil.virtual_memory().used
    swap_usage = psutil.swap_memory().used
    return memory_usage, swap_usage

# Base command template
base_command = "/home/noaa_gms/RFSS/Tools/processing/RFSS_classifyidentifyPCI_AWS1_AWS3_160ms_mat_CSV_vd8/run_RFSS_classifyidentifyPCI_AWS1_AWS3_160ms_mat_CSV_vd8.sh /usr/local/MATLAB/MATLAB_Runtime/R2023a /home/noaa_gms/RFSS/toDemod/temp{}/ /home/noaa_gms/RFSS/toDemod/temp{}/results/ '1' '0'"

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins} mins {secs} seconds"

def run_command(temp_id):
    command = base_command.format(temp_id, temp_id)
    start_time = time.time()
    try:
        process = subprocess.run(command, shell=True, text=True, capture_output=True)
        end_time = time.time()
        execution_time = end_time - start_time
        return temp_id, process.returncode, process.stderr, format_time(execution_time)
    except subprocess.SubprocessError as e:
        end_time = time.time()
        execution_time = end_time - start_time
        return temp_id, -1, str(e), format_time(execution_time)

for num_commands in range(1, 7):
    print(f"Running with num_commands = {num_commands}")

    max_memory_usage = 0
    max_swap_usage = 0

    overall_start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_commands) as executor:
        future_to_temp_id = {executor.submit(run_command, i): i for i in range(num_commands)}

        # Monitor memory usage while commands are running
        while any([not future.done() for future in future_to_temp_id.keys()]):
            current_memory_usage, current_swap_usage = get_memory_usage()
            max_memory_usage = max(max_memory_usage, current_memory_usage)
            max_swap_usage = max(max_swap_usage, current_swap_usage)
            time.sleep(1)  # Check every second

        for future in concurrent.futures.as_completed(future_to_temp_id):
            temp_id = future_to_temp_id[future]
            try:
                temp_id, returncode, error_message, execution_time = future.result()
                if returncode != 0:
                    print(f"Error occurred in command with temp{temp_id}:")
                    print(error_message)
                else:
                    print(f"Command with temp{temp_id} executed successfully.")
                print(f"Execution Time for temp{temp_id}: {execution_time}")
            except Exception as e:
                print(f"An exception occurred in command with temp{temp_id}: {e}")

    overall_end_time = time.time()
    overall_total_time = overall_end_time - overall_start_time

    print(f"Total Execution Time for num_commands = {num_commands}: {format_time(overall_total_time)}")
    print(f"Maximum Memory Usage during run: {max_memory_usage / (1024 ** 2):.2f} MB")
    print(f"Maximum Swap Usage during run: {max_swap_usage / (1024 ** 2):.2f} MB\n")
