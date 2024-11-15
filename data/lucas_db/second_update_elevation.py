#update missing elevation of updated elevation

import geemap
import ee
import pandas as pd

# Initialize Earth Engine
SERVICE_ACCOUNT = 'soil-project@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = '/Users/maxsonntag/Desktop/jsonkey_soil_project.json'
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

# Load the CSV file
file_path = "/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation_fixed.csv"
data = pd.read_csv(file_path)

# Define the elevation datasets
srtm_dataset = ee.Image("CGIAR/SRTM90_V4")
alos_dataset = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2").select("DSM")

# Function to get elevation, first trying SRTM and then falling back to ALOS if SRTM returns None
def get_elevation(lat, lon, buffer=100):
    point = ee.Geometry.Point(lon, lat).buffer(buffer)
    try:
        # Attempt SRTM retrieval first
        elevation = srtm_dataset.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=30
        ).get("elevation").getInfo()

        # If SRTM elevation is None, try ALOS
        if elevation is None:
            elevation = alos_dataset.median().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=30
            ).get("DSM").getInfo()

        # Return integer elevation if available, otherwise None
        if elevation is not None:
            return int(round(elevation))
        else:
            return None
    except Exception as e:
        print(f"Error fetching elevation for {lat}, {lon}: {e}")
        return None

# Check for missing values in the 'elevation' column and attempt to fetch them
for idx, row in data.iterrows():
    if pd.isnull(row['elevation']) or row['elevation'] == '':  # Check if elevation is missing
        print(f"Attempting to fetch elevation for missing value at index {idx}")
        elevation = get_elevation(row['lat'], row['long'])
        if elevation is not None:
            data.at[idx, 'elevation'] = elevation  # Update with the retrieved integer elevation
            print(f"Updated index {idx} with elevation: {elevation}")
        else:
            print(f"Could not retrieve elevation for index {idx}")

# Save the updated DataFrame to a new CSV file
output_file = "/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation_fixed.csv"
data.to_csv(output_file, index=False)
print(f"Updated CSV saved to {output_file}")