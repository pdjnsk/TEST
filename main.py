import requests
from shapely.geometry import Point, Polygon
import time
import os

# URL of the geojson file
url = "https://github.com/vatsimnetwork/vatspy-data-project/releases/download/v2408.2/Boundaries.geojson"

# List of FIR codes to check
fir_codes = ['VABF', 'VIDF', 'VOMF', 'VECF', 'VEGF']

# VATSIM data API URL
vatsim_api_url = "https://data.vatsim.net/v3/vatsim-data.json"

# Function to fetch all CID information
def fetch_all_cid_info():
    # Fetch VATSIM data to get all pilots and controllers
    vatsim_response = requests.get(vatsim_api_url)

    if vatsim_response.status_code == 200:
        vatsim_data = vatsim_response.json()

        # Check both pilots and controllers for the CIDs
        all_members = vatsim_data.get('pilots', []) + vatsim_data.get('controllers', [])

        return all_members
    else:
        print(f"Failed to fetch VATSIM data. Status code: {vatsim_response.status_code}")
        return []

# Function to check which FIR the CID is in
def get_fir_for_cid(fir_data, cid_lat, cid_lon):
    cid_point = Point(cid_lon, cid_lat)  # Create a Point object for the CID location

    for fir_code, features in fir_data.items():
        for feature in features:
            # Get the geometry of the FIR region
            geometry = feature['geometry']
            if geometry['type'] == 'Polygon':
                polygon = Polygon(geometry['coordinates'][0])  # Convert coordinates to Polygon object
                if polygon.contains(cid_point):
                    return fir_code
            elif geometry['type'] == 'MultiPolygon':
                for polygon_coords in geometry['coordinates']:
                    polygon = Polygon(polygon_coords[0])
                    if polygon.contains(cid_point):
                        return fir_code
    return None

# Function to fetch the FIR data
def fetch_fir_data():
    # Fetch the file from the URL for FIR data
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the GeoJSON data
        geojson_data = response.json()

        # Prepare FIR data for later use
        fir_data = {fir_code: [] for fir_code in fir_codes}

        # Iterate through each FIR code and store the FIR boundary data
        for idx, fir_code in enumerate(fir_codes):
            # Filter for features with the given FIR code in properties
            fir_data[fir_code] = [feature for feature in geojson_data['features'] if fir_code in feature['properties'].values()]

        return fir_data
    else:
        print(f"Failed to download the FIR data. Status code: {response.status_code}")
        return {}

# Function to check the FIR for all CIDs
def check_fir_for_all_cids():
    fir_data = fetch_fir_data()
    if not fir_data:
        return

    # Fetch all CID information
    all_members = fetch_all_cid_info()

    # Clear the console screen to avoid old data being printed
    os.system('cls' if os.name == 'nt' else 'clear')

    # Iterate through all members and check their FIR location
    for member_data in all_members:
        if 'latitude' in member_data and 'longitude' in member_data:
            cid_lat = member_data['latitude']
            cid_lon = member_data['longitude']
            cid = member_data['cid']
            callsign = member_data.get('callsign', 'N/A')

            # Check which FIR the CID is in
            fir_code = get_fir_for_cid(fir_data, cid_lat, cid_lon)

            if fir_code:
                # If the CID is within one of the specified FIR regions, print the details
                if fir_code in fir_codes:
                    print(f"CID {cid} Callsign: {callsign} is in FIR {fir_code}.")
                    print(f"Callsign: {callsign}")
                    print(f"FIR: {fir_code}")
                    print("-" * 30)

# Main loop to update every 15 seconds
def main():
    while True:
        check_fir_for_all_cids()  # Check and print CIDs in FIRs
        time.sleep(15)  # Wait for 15 seconds before refreshing the data

# Start the main loop
main()
