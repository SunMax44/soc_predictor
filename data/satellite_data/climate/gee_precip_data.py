import ee
import pandas as pd

# Initialize the Earth Engine API
ee.Initialize()

# Load your CSV file as a pandas DataFrame
df = pd.read_csv('path_to_your_file.csv')  # Replace with the actual path

# Convert DataFrame to a list of points with Earth Engine format
points = [ee.Feature(ee.Geometry.Point([row['longitude'], row['latitude']]), {'id': idx}) for idx, row in df.iterrows()]

# Create a FeatureCollection from points
points_fc = ee.FeatureCollection(points)

# Use TerraClimate for monthly precipitation data from April 2013 to March 2018
precipitation_dataset = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE').select('pr')
precipitation_filtered = precipitation_dataset.filterDate('2013-04-01', '2018-03-31')

# Sample monthly precipitation at each location
sampled_precipitation = precipitation_filtered.map(lambda image: image.sampleRegions(
    collection=points_fc,
    scale=4000,  # Use 4 km scale for TerraClimate's resolution
    geometries=True
))

# Flatten the collection for export
precipitation_flattened = sampled_precipitation.flatten()

# Export to Google Drive
task = ee.batch.Export.table.toDrive(
    collection=precipitation_flattened,
    description='MonthlyPrecipitationMeans_TerraClimate_2013_2018',
    folder='EarthEngineExports',
    fileNamePrefix='monthly_precipitation_means_2013_2018',
    fileFormat='CSV'
)

# Start the export task
task.start()

print("Export started. Check Google Drive in EarthEngineExports folder.")
