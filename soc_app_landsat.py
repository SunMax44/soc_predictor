#this code runs the streamlit with landsat data, which uses a 30x30m per pixel resolution
#pro: data dates bck until 1980
#con: -lower resolution limits ability to mask cloudy parts and uses other
#con: only each 16 days images also lower ability to work around clouds

import streamlit as st
import ee
import pandas as pd
from datetime import datetime, timedelta

# Initialize Earth Engine with service account credentials
SERVICE_ACCOUNT = 'soil-project-admin@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = 'key_soc_project.json'  # Adjust this path to the JSON key file location
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

def mask_clouds(image):
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 5).eq(0))
    return image.updateMask(cloud_mask)

def calculate_indices(image):
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    ndmi = image.normalizedDifference(['SR_B5', 'SR_B6']).rename('NDMI')
    bsi = image.expression(
        '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))', {
            'SWIR': image.select('SR_B6'),
            'RED': image.select('SR_B4'),
            'NIR': image.select('SR_B5'),
            'BLUE': image.select('SR_B2')
        }).rename('BSI')
    return image.addBands([ndvi, ndmi, bsi])

def fetch_monthly_indices(lat, lon):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=3*365)
    date_ranges = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    data = []
    
    for start in date_ranges:
        # Expand each month to ±15 days around the month
        start_extended = start - timedelta(days=15)
        end_extended = start + pd.DateOffset(months=1) + timedelta(days=15) - timedelta(days=1)
        
        # Filter for the extended date range
        landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                    .filterDate(start_extended.strftime('%Y-%m-%d'), end_extended.strftime('%Y-%m-%d')) \
                    .filterBounds(ee.Geometry.Point(lon, lat)) \
                    .filter(ee.Filter.lt('CLOUD_COVER', 60))
        
        landsat = landsat.map(mask_clouds).map(calculate_indices)
        
        # If no images are left after masking, append NaNs for the month
        if landsat.size().getInfo() == 0:
            data.append({'date': start.strftime('%Y-%m-%d'), 'NDVI': None, 'NDMI': None, 'BSI': None})
            continue
        
        # Average over all images within the extended date range to create a composite
        monthly_composite = landsat.mean().set('date', start.strftime('%Y-%m-%d'))
        
        # Sample the indices at the location with a 60m buffer
        point = ee.Geometry.Point(lon, lat)
        result = monthly_composite.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point.buffer(60),
            scale=30
        ).getInfo()
        
        # Filter to keep only NDVI, NDMI, and BSI
        filtered_result = {
            'date': start.strftime('%Y-%m-%d'),
            'NDVI': result.get('NDVI'),
            'NDMI': result.get('NDMI'),
            'BSI': result.get('BSI')
        }
        
        data.append(filtered_result)
    
    df = pd.DataFrame(data)
    return df

# Streamlit app for user input and data fetching
st.title("Monthly Vegetation Indices with Cloud Masking and Expanded Temporal Window")

lat = st.number_input("Latitude", format="%.6f", value=54.8599)
lon = st.number_input("Longitude", format="%.6f", value=8.4114)

if st.button("Fetch Data"):
    df = fetch_monthly_indices(lat, lon)
    if not df.empty:
        st.success("Data fetched successfully!")
        st.write(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download data as CSV", data=csv, file_name="monthly_indices.csv", mime="text/csv")
    else:
        st.warning("No data available for the specified location and time range.")