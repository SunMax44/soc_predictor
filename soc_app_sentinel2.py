#this streamlit app uses the sentinel-2 satellite data with some pros:
# images very 5 days and resolution of 10m allow to work around cloudy seasons a lot better and
# get better / more consistant data
#con: only dates back until 2015, so maybe not suited for model training


#code retrieves data for the past 3 years atm, could be changed to 5
import streamlit as st
import ee
import pandas as pd
from datetime import datetime, timedelta

# Initialize Earth Engine with service account credentials
SERVICE_ACCOUNT = 'soil-project-admin@ee-maxsonntag4.iam.gserviceaccount.com'
KEY_PATH = 'key_soc_project.json'  # Adjust this path to the JSON key file location
EE_CREDENTIALS = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(EE_CREDENTIALS)

def mask_clouds_sentinel2(image):
    # Use the SCL band for cloud masking: 3 = clear, 4 = vegetation, 5 = not water, 6 = non-cloud shadow
    scl = image.select('SCL')
    cloud_mask = scl.eq(3).Or(scl.eq(4)).Or(scl.eq(5)).Or(scl.eq(6))
    return image.updateMask(cloud_mask)

def calculate_indices_sentinel2(image):
    # Sentinel-2 bands for indices
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')  # NIR (B8) and Red (B4)
    ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')  # NIR (B8) and SWIR1 (B11)
    bsi = image.expression(
        '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))', {
            'SWIR': image.select('B11'),
            'RED': image.select('B4'),
            'NIR': image.select('B8'),
            'BLUE': image.select('B2')
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
        
        # Filter the Sentinel-2 collection for the extended date range
        sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR') \
                    .filterDate(start_extended.strftime('%Y-%m-%d'), end_extended.strftime('%Y-%m-%d')) \
                    .filterBounds(ee.Geometry.Point(lon, lat)) \
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))
        
        # Apply cloud masking and calculate indices
        sentinel2 = sentinel2.map(mask_clouds_sentinel2).map(calculate_indices_sentinel2)
        
        # If no images are left after masking, append NaNs for the month
        if sentinel2.size().getInfo() == 0:
            data.append({'date': start.strftime('%Y-%m-%d'), 'NDVI': None, 'NDMI': None, 'BSI': None})
            continue
        
        # Create a monthly composite by averaging all images in the extended date range
        monthly_composite = sentinel2.mean().set('date', start.strftime('%Y-%m-%d'))
        
        # Sample the indices at the location with a 60m buffer
        point = ee.Geometry.Point(lon, lat)
        result = monthly_composite.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point.buffer(60),
            scale=10  # Sentinel-2 has a 10m resolution for the bands used
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
st.title("Monthly Vegetation Indices with Sentinel-2 Cloud Masking and Expanded Temporal Window")

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
