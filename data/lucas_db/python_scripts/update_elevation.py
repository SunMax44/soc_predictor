import geemap
import ee
import pandas as pd

# Initialize Earth Engine
SERVICE_ACCOUNT = 'soil-project@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = '/Users/maxsonntag/Desktop/jsonkey_soil_project.json'
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

# Load your CSV file
file_path = "/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation.csv"  # replace with your CSV file path
data = pd.read_csv(file_path)

# Define the elevation dataset (using SRTM in this example)
elevation_dataset = ee.Image("CGIAR/SRTM90_V4")

# Function to get elevation for a given point with error handling
def get_elevation(lat, lon):
    point = ee.Geometry.Point(lon, lat)
    # Use try-except to handle cases where elevation might not be available
    try:
        elevation = elevation_dataset.sample(point, 30).first().get("elevation")
        # Check if elevation was successfully retrieved
        if elevation is None:
            return None
        return elevation.getInfo()
    except Exception as e:
        print(f"Error fetching elevation for {lat}, {lon}: {e}")
        return None

# Retrieve elevation for each latitude-longitude pair
elevations = []
for _, row in data.iterrows():
    elevation = get_elevation(row['lat'], row['long'])
    elevations.append(elevation)

# Add the retrieved elevations to the DataFrame
data['elevation'] = elevations


# Save to a new CSV file
output_file = "/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation_retrieved.csv"
data.to_csv(output_file, index=False)
print(f"Elevation data saved to {output_file}")
