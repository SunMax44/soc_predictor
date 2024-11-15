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
    scl = image.select('SCL')
    cloud_mask = scl.eq(3).Or(scl.eq(4)).Or(scl.eq(5)).Or(scl.eq(6))
    return image.updateMask(cloud_mask)

def calculate_indices_landsat(image):
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')  # NIR (SR_B5) and Red (SR_B4)
    ndmi = image.normalizedDifference(['SR_B5', 'SR_B6']).rename('NDMI')  # NIR (SR_B5) and SWIR1 (SR_B6)
    bsi = image.expression(
        '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))', {
            'SWIR': image.select('SR_B6'),
            'RED': image.select('SR_B4'),
            'NIR': image.select('SR_B5'),
            'BLUE': image.select('SR_B2')
        }).rename('BSI')
    soci = image.expression('BLUE / (GREEN * RED)', {
        'BLUE': image.select('SR_B2'),
        'GREEN': image.select('SR_B3'),
        'RED': image.select('SR_B4')
    }).rename('SOCI')
    
    return image.addBands([ndvi, ndmi, bsi, soci])

def fetch_monthly_indices_landsat(lat, lon, cloud_threshold=80):
    # Define date range for the last 5 years with 15-day intervals
    end_date = datetime.today().replace(day=1) - timedelta(days=1)
    start_date = end_date - timedelta(days=5*365)
    date_ranges = pd.date_range(start=start_date, end=end_date, freq='15D')
    
    data = []
    
    for start in date_ranges:
        # 1-month rolling window (±15 days) for each 15-day interval
        start_extended = start - timedelta(days=15)
        end_extended = start + timedelta(days=15)
        
        # Use Landsat 8 collection with cloud threshold filtering only
        landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
                   .filterDate(start_extended.strftime('%Y-%m-%d'), end_extended.strftime('%Y-%m-%d')) \
                   .filterBounds(ee.Geometry.Point(lon, lat)) \
                   .filter(ee.Filter.lte('CLOUD_COVER', cloud_threshold)) \
                   .select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'QA_PIXEL'])  # Select required bands
        
        # Cloud masking without shadow masking
        def mask_clouds_landsat(image):
            qa = image.select('QA_PIXEL')
            cloud = qa.bitwiseAnd(1 << 4).eq(0)  # Mask clouds only
            return image.updateMask(cloud)
        
        # Apply cloud masking and calculate indices
        landsat = landsat.map(mask_clouds_landsat).map(calculate_indices_landsat)
        
        # If no images remain after masking, add NaNs for the interval
        if landsat.size().getInfo() == 0:
            data.append({'date': start.strftime('%Y-%m-%d'), 'NDVI': None, 'NDMI': None, 'BSI': None, 'SOCI': None})
            continue
        
        # Composite the images over 1 month
        composite = landsat.mean().set('date', start.strftime('%Y-%m-%d'))
        
        # Sample the indices at the location with a 30m buffer and 30m resolution
        point = ee.Geometry.Point(lon, lat)
        result = composite.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point.buffer(30),
            scale=30
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

def fetch_climate_data(lat, lon):
    # Define the point of interest
    point = ee.Geometry.Point(lon, lat)
    
    # Retrieve the average temperature for 2023 from TerraClimate
    temp_2023 = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") \
                .select(['tmmn', 'tmmx']) \
                .filterDate('2023-01-01', '2023-12-31') \
                .filterBounds(point)
    
    # Monthly precipitation over the last 3 years for standard deviation calculation
    end_date = datetime.today().replace(day=1) - timedelta(days=1)
    start_date = end_date - timedelta(days=3*365)  # Only 3 years back now
    
    monthly_precip = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") \
                      .select('pr') \
                      .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
                      .filterBounds(point)
    
    precip_data = []
    
    # Calculate the average temperature from tmmn and tmmx for 2023
    temp_2023_img = temp_2023.mean()  # Annual composite for 2023
    tmmn = temp_2023_img.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=4000).get('tmmn')
    tmmx = temp_2023_img.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=4000).get('tmmx')
    
    if tmmn is not None and tmmx is not None:
        tmmn_val = tmmn.getInfo()
        tmmx_val = tmmx.getInfo()
        mean_temperature = (tmmn_val + tmmx_val) / 2
    else:
        mean_temperature = None  # Handle missing data gracefully
    
    # Retrieve and process monthly precipitation data for the past 3 years
    for image in monthly_precip.toList(monthly_precip.size()).getInfo():
        img = ee.Image(image['id'])
        precip = img.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=4000).get('pr')
        precip_data.append(precip.getInfo() if precip is not None else 0)
    
    # Calculate mean and standard deviation for monthly precipitation
    mean_precip = sum(precip_data) / len(precip_data) if precip_data else 0
    std_precip = (sum((x - mean_precip) ** 2 for x in precip_data) / len(precip_data)) ** 0.5 if precip_data else 0

    return mean_precip, std_precip, mean_temperature

# Streamlit app
st.title("Fetch Data Separately for Analysis")

lat = st.number_input("Latitude", format="%.6f", value=54.8599)
lon = st.number_input("Longitude", format="%.6f", value=8.4114)
elevation = st.number_input("Elevation (meters)", format="%.1f", value=50.0, help="Enter elevation if known.")

# Fetch Indices Button
if st.button("Fetch Indices"):
    df, index_stats = fetch_monthly_indices_landsat(lat, lon)
    if not df.empty:
        st.success("Indices fetched successfully!")
        st.write("Indices Statistics:", index_stats)
        
        # Display and offer download of data as JSON
        json_data_indices = pd.Series(index_stats).to_json()
        st.download_button(label="Download Indices Data as JSON", data=json_data_indices, file_name="indices_data.json", mime="application/json")
    else:
        st.warning("No indices data available for the specified location and time range.")

# Fetch Climate Data Button
if st.button("Fetch Climate Data"):
    mean_precip, std_precip, mean_temp = fetch_climate_data(lat, lon)
    climate_stats = {
        'mean_monthly_precip': mean_precip,
        'std_monthly_precip': std_precip,
        'mean_annual_temp': mean_temp
    }
    st.success("Climate data fetched successfully!")
    st.write("Climate Statistics:", climate_stats)
    
    # Display and offer download of data as JSON
    json_data_climate = pd.Series(climate_stats).to_json()
    st.download_button(label="Download Climate Data as JSON", data=json_data_climate, file_name="climate_data.json", mime="application/json")
