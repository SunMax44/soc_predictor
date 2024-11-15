import ee
import pandas as pd

# Initialize Earth Engine
SERVICE_ACCOUNT = 'soil-project@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = '/Users/maxsonntag/Desktop/jsonkey_soil_project.json'
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

# Load your CSV file with ~10,000 locations
data = pd.read_csv('/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/date_location_lucas_ag.csv')

# Create a FeatureCollection from the location data (limit to 10 locations for testing)
features = []
for _, row in data.head(10).iterrows():  # limit to first 10 locations for testing
    point = ee.Geometry.Point([row['long'], row['lat']])
    feature = ee.Feature(point)
    features.append(feature)

# Define the FeatureCollection of all points
fc = ee.FeatureCollection(features)

# Define the date range for the entire year 2017
start_date = '2017-01-01'
end_date = '2017-12-31'

# Using WorldClim data for temperature (annual mean temperature grid)
temperature = ee.Image("WORLDCLIM/V1/1_4/BIOMASS_1").select('bio01')  # bio01 is the annual mean temperature

# Using TerraClimate data for precipitation (monthly mean precipitation for 2013-2018)
precipitation = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE").select('pr') \
                 .filterDate('2013-04-01', '2018-03-31')

# Function to add climate data (temperature and precipitation) to each feature
def add_climate_data(feature):
    # Get the annual mean temperature for 2017
    temp_2017 = temperature.reduceRegion(reducer=ee.Reducer.mean(), geometry=feature.geometry(), scale=5000).get('bio01')
    
    # Get the monthly mean precipitation for the period (2013-2018)
    precip_monthly = precipitation.mean().reduceRegion(reducer=ee.Reducer.mean(), geometry=feature.geometry(), scale=4000).get('pr')
    
    return feature.set({
        'mean_temp_2017': temp_2017,
        'mean_precip_monthly': precip_monthly
    })

# Apply the climate data function to the FeatureCollection
fc_with_climate = fc.map(add_climate_data)

# Export the 2017 temperature data
task_temp = ee.batch.Export.table.toDrive(
    collection=fc_with_climate,
    description='TemperatureDataExport',
    fileFormat='CSV',
    fileNamePrefix='mean_temperature_2017',
    folder='EarthEngineExports'
)

# Start the temperature task
task_temp.start()

# Export the monthly precipitation data
task_precip = ee.batch.Export.table.toDrive(
    collection=fc_with_climate,
    description='PrecipitationDataExport',
    fileFormat='CSV',
    fileNamePrefix='mean_precipitation_monthly',
    folder='EarthEngineExports'
)

# Start the precipitation task
task_precip.start()

# Print task status once completed
print(f"Temperature export task status: {task_temp.status()}")
print(f"Precipitation export task status: {task_precip.status()}")
