from RsInstrument import *

resource_string_1 = 'TCPIP::192.168.1.101::hislip0'
option_string_force_rs_visa = 'SelectVisa=rs'
RsInstrument.assert_minimum_version('1.53.0')

def list_directory_content_and_download_files():
    try:
        # Open the instrument connection
        instr = RsInstrument(resource_string_1, False, False, option_string_force_rs_visa) #(Resource, ID Query, Reset, Options)

        # Set the current directory
        instr.write('MMEM:CDIR "c:\\R_S\\Instr\\user\\RFSS\\"')

        # List the directory content
        response = instr.query('MMEM:CAT?')

        # Process the response and print the content
        content_list = response.replace('\'', '').split(',')
        print("Directory content:")
        for item in content_list:
            print(item)

            # Download each file in the directory (skip directories)
            if not item.endswith('/'):  # Skip directories
                local_filename = '/home/noaa_gms/RFSS/Received/' + item  # Set the destination path on your PC
                instrument_filename = 'c:\\R_S\\Instr\\user\\RFSS\\' + item  # Set the instrument file path

                try:
                    # Download the file
                    data = instr.read_file_from_instrument_to_pc(instrument_filename, local_filename)

                    # Check if data is not None before writing to the file
                    if data is not None:
                        with open(local_filename, 'wb') as f:
                            f.write(data)
                        print(f"Downloaded file '{item}' to '{local_filename}'")
                    else:
                        print('')

                except Exception as e:
                    print(f"Error while downloading file '{item}': {str(e)}")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close the instrument connection
        instr.close()

if __name__ == "__main__":
    list_directory_content_and_download_files()