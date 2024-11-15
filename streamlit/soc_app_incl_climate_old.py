#this streamlit app uses the sentinel-2 satellite data with some pros:
# images very 5 days and resolution of 10m allow to work around cloudy seasons a lot better and
# get better / more consistant data
#con: only dates back until 2015, so maybe not suited for model training


# Streamlit app to fetch vegetation indices, SOCI, temperature, and precipitation for a single location

import streamlit as st
import ee
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import linregress

# Initialize Earth Engine with service account credentials
SERVICE_ACCOUNT = 'soil-project@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = '/Users/maxsonntag/Desktop/jsonkey_soil_project.json'
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

def mask_clouds_sentinel2(image):
    # Use the SCL band for cloud masking: 3 = clear, 4 = vegetation, 5 = not water, 6 = non-cloud shadow
    scl = image.select('SCL')
    cloud_mask = scl.eq(3).Or(scl.eq(4)).Or(scl.eq(5)).Or(scl.eq(6))
    return image.updateMask(cloud_mask)

def calculate_indices_sentinel2(image):
    # Calculate NDVI, NDMI, BSI, and SOCI (Soil Organic Carbon Index)
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')
    bsi = image.expression(
        '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))', {
            'SWIR': image.select('B11'),
            'RED': image.select('B4'),
            'NIR': image.select('B8'),
            'BLUE': image.select('B2')
        }).rename('BSI')
    soci = image.expression('BLUE / (GREEN * RED)', {
        'BLUE': image.select('B2'),
        'GREEN': image.select('B3'),
        'RED': image.select('B4')
    }).rename('SOCI')
    return image.addBands([ndvi, ndmi, bsi, soci])

def fetch_climate_data(lat, lon):
    # Define the time range for the last 5 years up to the last full month
    today = datetime.today().replace(day=1)
    end_date = today - timedelta(days=1)
    start_date = end_date - timedelta(days=5*365)
    
    precip_data = []
    temperature_data = []
    
    # Define the point of interest
    point = ee.Geometry.Point(lon, lat)
    
    # Set up the monthly precipitation and temperature ImageCollection from TerraClimate
    monthly_precip = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") \
                      .select('pr') \
                      .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                      .filterBounds(point)
    
    monthly_temp = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") \
                    .select(['tmmn', 'tmmx']) \
                    .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                    .filterBounds(point)
    
    # Retrieve monthly precipitation and temperature
    for image in monthly_precip.toList(monthly_precip.size()).getInfo():
        img = ee.Image(image['id'])
        precip = img.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=4000).get('pr')
        precip_data.append(precip if precip is not None else 0)
    
    for image in monthly_temp.toList(monthly_temp.size()).getInfo():
        img = ee.Image(image['id'])
        tmmn = img.select('tmmn').reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=4000).get('tmmn')
        tmmx = img.select('tmmx').reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=4000).get('tmmx')
        
        if tmmn is not None and tmmx is not None:
            temperature_data.append((tmmn + tmmx) / 2)
    
    # Calculate mean and std for monthly precipitation data over 5 years
    mean_precip = sum(precip_data) / len(precip_data) if precip_data else 0
    std_precip = (sum((x - mean_precip) ** 2 for x in precip_data) / len(precip_data)) ** 0.5 if precip_data else 0
    
    # Calculate mean annual temperature over 5 years
    mean_temperature = sum(temperature_data) / len(temperature_data) if temperature_data else None

    return mean_precip, std_precip, mean_temperature

def fetch_quarterly_simple_indices(lat, lon, cloud_threshold=80):
    # Define date range for the last 5 years
    end_date = datetime.today().replace(day=1) - timedelta(days=1)
    start_date = end_date - timedelta(days=5*365)
    date_ranges = pd.date_range(start=start_date, end=end_date, freq='QS')  # Retrieve data quarterly
    
    data = []
    
    for start in date_ranges:
        # Define a target date roughly in the middle of the quarter
        target_date = start + pd.DateOffset(months=1, days=15)
        
        # Filter the Sentinel-2 collection around the target date and by cloud cover
        sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR') \
                    .filterDate(target_date.strftime('%Y-%m-%d'), (target_date + timedelta(days=15)).strftime('%Y-%m-%d')) \
                    .filterBounds(ee.Geometry.Point(lon, lat)) \
                    .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold)) \
                    .select(['B2', 'B3', 'B4', 'B8', 'B11', 'SCL', 'QA60'])  # Only necessary bands
        
        # Retrieve the first available image in this range
        image = sentinel2.first()
        
        # If there are no suitable images, append NaNs for this quarter
        if image is None:
            data.append({'date': start.strftime('%Y-%m-%d'), 'NDVI': None, 'NDMI': None, 'BSI': None, 'SOCI': None})
            continue
        
        # Sample the indices at the location with a 30m buffer and 30m scale
        point = ee.Geometry.Point(lon, lat)
        result = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point.buffer(30),  # 30m buffer
            scale=30  # 30m resolution
        ).getInfo()
        
        # Extract only NDVI, NDMI, BSI, and SOCI
        filtered_result = {
            'date': start.strftime('%Y-%m-%d'),
            'NDVI': result.get('NDVI'),
            'NDMI': result.get('NDMI'),
            'BSI': result.get('BSI'),
            'SOCI': result.get('SOCI')
        }
        
        data.append(filtered_result)
    
    df = pd.DataFrame(data)

    # Calculate mean, std, and trend for each index over the 5 years
    stats = {}
    for index in ['NDVI', 'NDMI', 'BSI', 'SOCI']:
        stats[f'{index}_mean'] = df[index].mean()
        stats[f'{index}_std'] = df[index].std()
        valid_data = df.dropna(subset=[index])
        stats[f'{index}_trend'] = linregress(np.arange(len(valid_data)), valid_data[index])[0] if not valid_data.empty else None
    
    return df, stats


# Streamlit app for user input and data fetching
st.title("Monthly Vegetation Indices, SOCI, and Climate Data with Sentinel-2 Cloud Masking")

lat = st.number_input("Latitude", format="%.6f", value=54.8599)
lon = st.number_input("Longitude", format="%.6f", value=8.4114)
elevation = st.number_input("Elevation (meters)", format="%.1f", value=50.0, help="Enter elevation if known to avoid retrieval errors.")

if st.button("Fetch Data"):
    df, index_stats = fetch_quarterly_simple_indices(lat, lon)
    mean_precip, std_precip, mean_temp = fetch_climate_data(lat, lon)
    
    if not df.empty:
        st.success("Data fetched successfully!")
        
        # Combine data into a single dictionary for dynamic use
        model_input_data = {
            'elevation': elevation,
            'mean_monthly_precip': mean_precip,
            'std_monthly_precip': std_precip,
            'mean_annual_temp': mean_temp,
            **index_stats
        }
        
        # Display the inputs for the model
        st.write("Model Input Data:", model_input_data)
        
        # Offer download as JSON
        json_data = pd.Series(model_input_data).to_json()
        st.download_button(label="Download data as JSON", data=json_data, file_name="model_input_data.json", mime="application/json")
    else:
        st.warning("No data available for the specified location and time range.")
