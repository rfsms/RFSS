import pandas as pd
import numpy as np
import folium
from branca.colormap import linear

# Function to convert azimuth angle to lat, long offset
def azimuth_to_offsets(azimuth, base_lat, base_long, distance=0.008):
    azimuth_rad = np.deg2rad(azimuth)
    d_lat = distance * np.cos(azimuth_rad)
    d_long = distance * np.sin(azimuth_rad)
    return base_lat + d_lat, base_long + d_long

# Function to calculate the radius based on power level
def calculate_radius(power, min_power, max_power, min_radius=3, max_radius=10):
    normalized_power = (power - min_power) / (max_power - min_power)
    radius = normalized_power * (max_radius - min_radius) + min_radius
    return radius

# Function to create the map with markers and lines
def create_power_levels_map(data_path, base_lat, base_long, power_threshold):
    # Load the data
    data = pd.read_csv(data_path)

    # Reshape the dataset
    reshaped_data = data.melt(id_vars=['Frequency (MHz)'], var_name='Azimuth', value_name='Power')
    reshaped_data['Azimuth'] = reshaped_data['Azimuth'].str.extract('(\d+)$').astype(int)

    # Aggregate the data by finding the peak power for each azimuth
    aggregated_data = reshaped_data.groupby('Azimuth')['Power'].max().reset_index()

    # Filter data based on the power threshold
    filtered_data = aggregated_data[aggregated_data['Power'] > power_threshold]

    azimuths = filtered_data['Azimuth']
    power_values = filtered_data['Power']

    # Create a color map
    min_power = min(power_values)
    max_power = max(power_values)
    colormap = linear.YlOrRd_09.scale(min_power, max_power)

    # Create the map
    map = folium.Map(location=[base_lat, base_long], zoom_start=13)
    colormap.caption = "Power Level Intensity"
    map.add_child(colormap)

    # Add markers and lines
    for azimuth, power in zip(azimuths, power_values):
        lat, long = azimuth_to_offsets(azimuth, base_lat, base_long)
        color = colormap(power)
        radius = calculate_radius(power, min_power, max_power, min_radius=5, max_radius=20)
        popup_text = f"Power: {power:.2f} dB, Azimuth: {azimuth}°"
        popup = folium.Popup(popup_text, max_width=300)
        folium.CircleMarker(location=[lat, long], radius=radius, color=color, fill=True, fill_color=color, popup=popup).add_to(map)
        folium.PolyLine([(base_lat, base_long), (lat, long)], color='gray', weight=1, opacity=0.5).add_to(map)

    return map

data_path = '/home/noaa_gms/RFSS/commutationData/2023_11_01_221855/20231101_221855.csv'
base_lat = 25.734725  # Replace with your base latitude
base_long = -80.162317  # Replace with your base longitude
power_threshold = -80  # Replace with your desired power level threshold
map = create_power_levels_map(data_path, base_lat, base_long, power_threshold)
map.save('output_map.html')