# Import necessary libraries
import ee
import pandas as pd
from datetime import datetime, timedelta

# Initialize Earth Engine
SERVICE_ACCOUNT = 'soil-project@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = '/Users/maxsonntag/Desktop/jsonkey_soil_project.json'
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

# Cloud masking function for Landsat, keeping both cloud and shadow masking
def mask_clouds_landsat(image):
    # Mask based on QA_PIXEL band (bitmask to identify clouds and shadows)
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 4).eq(0).And(qa.bitwiseAnd(1 << 5).eq(0))  # Clear of both clouds and shadows
    return image.updateMask(cloud_mask)

# Indices calculation function adapted for Landsat 8
def calculate_indices_landsat(image):
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    ndmi = image.normalizedDifference(['SR_B5', 'SR_B6']).rename('NDMI')
    bsi = image.expression(
        '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))', {
            'SWIR': image.select('SR_B6'),
            'RED': image.select('SR_B4'),
            'NIR': image.select('SR_B5'),
            'BLUE': image.select('SR_B2')
        }).rename('BSI')
    soci = image.select('SR_B2').divide(image.select('SR_B3').multiply(image.select('SR_B4'))).rename('SOCI')
    return image.addBands([ndvi, ndmi, bsi, soci])

# Quarterly data retrieval and export function for running in batches of two quarters
def export_quarterly_composites_to_drive(data, start_dates):
    points = ee.FeatureCollection([
        ee.Feature(ee.Geometry.Point(row['long'], row['lat']), {'sample_date': row['sample_date']})
        for _, row in data.iterrows()
    ])

    for start in start_dates:
        # Define end date for the quarterly period
        end = start + pd.DateOffset(months=3)

        # Filter Landsat collection and apply cloud threshold and masking
        landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                   .filterDate(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
                   .filterBounds(points.geometry())
                   .filter(ee.Filter.lt('CLOUD_COVER_LAND', 70))  # 70% cloud threshold
                   .map(mask_clouds_landsat)
                   .map(calculate_indices_landsat))

        # Quarterly mean composite for calculated indices only
        quarterly_composite = landsat.select(['NDVI', 'NDMI', 'BSI', 'SOCI']).mean()

        # Create the export task with 30m buffer
        task = ee.batch.Export.table.toDrive(
            collection=points.map(lambda feature: feature.set(
                quarterly_composite.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=feature.geometry().buffer(30),  # Buffer size set to 30m
                    scale=30
                )
            )),
            description=f"export_all_locations_{start.strftime('%Y_%m')}",
            folder='EarthEngineExports',
            fileNamePrefix=f"output_all_locations_{start.strftime('%Y_%m')}",
            fileFormat='CSV'
        )
        task.start()
        print(f"Started export for period starting {start.strftime('%Y-%m-%d')}.")

# Main execution block for quarterly batches with pause
if __name__ == '__main__':
    # Load the initial CSV with 19,000 locations
    data = pd.read_csv('/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/date_location_lucas.csv')

    # Determine the last sample date
    last_sample_date = datetime.strptime(data['sample_date'].max(), '%Y-%m-%d')
    
    # Define start and end dates for the second 2.5 years
    midpoint_date = last_sample_date - timedelta(days=2.5*365)  # 2.5 years before the last sample date
    end_date = last_sample_date  # Latest sample date

    # Generate a list of quarterly start dates from midpoint_date to end_date
    date_ranges = pd.date_range(start=midpoint_date, end=end_date, freq='QS')

    # Run quarterly exports in batches of two
    for i in range(0, len(date_ranges), 2):
        # Get the next two quarters
        batch_dates = date_ranges[i:i+2]
        export_quarterly_composites_to_drive(data, batch_dates)
        
        # Pause and wait for user input before continuing to the next batch
        input("Press Enter after the current batch of two quarters completes to continue to the next batch...")
