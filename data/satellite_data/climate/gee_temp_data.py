import ee
import pandas as pd

# Initialize the Earth Engine API
SERVICE_ACCOUNT = 'soil-project@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = '/Users/maxsonntag/Desktop/jsonkey_soil_project.json'
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

# Load your CSV file as a pandas DataFrame
# Assuming 'latitude' and 'longitude' are the column names for coordinates
df = pd.read_csv('/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/date_location_lucas_ag.csv')

# Convert DataFrame to a list of points with Earth Engine format
points = [ee.Feature(ee.Geometry.Point([row['long'], row['lat']]), {'id': idx}) for idx, row in df.iterrows()]

# Create a FeatureCollection from points
points_fc = ee.FeatureCollection(points)

# Define the temperature dataset
temperature_dataset = ee.ImageCollection('ECMWF/ERA5/DAILY')  # Replace with the preferred dataset if necessary
temperature_2017 = temperature_dataset.filterDate('2017-01-01', '2017-12-31').select('mean_2m_air_temperature')

# Calculate the mean temperature over 2017 and convert from Kelvin to Celsius
annual_mean_2017 = temperature_2017.mean().subtract(273.15).rename('annual_mean_temperature_2017_C')


# Sample the mean temperature at each location
temperature_at_points = annual_mean_2017.sampleRegions(
    collection=points_fc,
    scale=5000,  # Adjust scale based on dataset resolution and requirements
    geometries=True
)

# Set up the export to Google Drive
task = ee.batch.Export.table.toDrive(
    collection=temperature_at_points,
    description='AnnualMeanTemperature2017',
    folder='EarthEngineExports',
    fileNamePrefix='annual_mean_temperature_2017',
    fileFormat='CSV'
)

# Start the export task
task.start()

print("Export started. Check Google Drive in EarthEngineExports folder.")
