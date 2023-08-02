import csv

def replace_satellite(satellite):
    replacements = {
        "NOAA 15": "NOAA-15",
        "NOAA 18": "NOAA-18",
        "NOAA 19": "NOAA-19"
    }
    return replacements.get(satellite, satellite)

# Read the file and extract specific columns from each row of the table
with open("report.txt", "r") as file:
    lines = file.readlines()

table_started = False
columns_to_print = [1, 2, 3]  # Column indices: 1 for Satellite, 2 for AOS, and 3 for LOS

# Calculate the number of rows to print excluding the header and last 5 rows
rows_to_print = len(lines) - 5

# Create a list to store the extracted data
data = []

for i, line in enumerate(lines):
    if line.strip().startswith("----"):
        table_started = True
        continue  # Skip the line with "----" as it's just a table separator

    if table_started and i < rows_to_print:
        satellite = line[5:20].strip()
        aos = line[20:43].strip()
        los = line[43:66].strip()

        # Replace the satellite name if it matches the specified patterns
        satellite = replace_satellite(satellite)

        data.append([satellite, aos, los])

# Write the data to a CSV file
with open("report.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Satellite", "AOS", "LOS"])
    csv_writer.writerows(data)
