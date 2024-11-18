import streamlit as st
import pandas as pd
import numpy as np
import ee
import pickle
from datetime import datetime, timedelta
import os
import json

# Initialize Earth Engine with service account credentials
# Retrieve the JSON key from secrets
GEE_CREDENTIALS = json.loads(st.secrets["GEE_CREDENTIALS_JSON"])

# Write the JSON to a temporary file
with open("temp-gee-key.json", "w") as key_file:
    json.dump(GEE_CREDENTIALS, key_file)

# Initialize Earth Engine
EE_CREDENTIALS = ee.ServiceAccountCredentials(GEE_CREDENTIALS["client_email"], "temp-gee-key.json")
ee.Initialize(EE_CREDENTIALS)

# Load the trained model
with open("ml_model/tuned_lightgbm_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

# Load frequency and mean encodings for 'main_vegetation_type'
freq_encoding = np.load("main_vegetation_type_freq_encoding.npy", allow_pickle=True).item()
mean_encoding = np.load("main_vegetation_type_mean_encoding.npy", allow_pickle=True).item()

# Function to mask clouds in Landsat images
def mask_clouds_landsat(image):
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 5).eq(0).And(qa.bitwiseAnd(1 << 3).eq(0))
    return image.updateMask(cloud_mask)

# Function to calculate NDVI, NDMI, BSI, and SOCI
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
    soci = image.expression('BLUE / (GREEN * RED)', {
        'BLUE': image.select('SR_B2'),
        'GREEN': image.select('SR_B3'),
        'RED': image.select('SR_B4')
    }).rename('SOCI')
    return image.addBands([ndvi, ndmi, bsi, soci])

# Function to retrieve Landsat data and calculate indices
def fetch_quarterly_simple_indices(lat, lon, cloud_threshold=80):
    end_date = datetime.today().replace(day=1) - timedelta(days=1)
    start_date = end_date - timedelta(days=5*365)
    date_ranges = pd.date_range(start=start_date, end=end_date, freq='QS')
    
    data = []
    for start in date_ranges:
        target_date = start + pd.DateOffset(months=1, days=15)
        
        landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                    .filterDate(target_date.strftime('%Y-%m-%d'), (target_date + timedelta(days=15)).strftime('%Y-%m-%d')) \
                    .filterBounds(ee.Geometry.Point(lon, lat)) \
                    .filter(ee.Filter.lte('CLOUD_COVER', cloud_threshold)) \
                    .map(mask_clouds_landsat) \
                    .map(calculate_indices_landsat) \
                    .select(['NDVI', 'NDMI', 'BSI', 'SOCI'])
        
        image = landsat.first()
        
        if not image or image.getInfo() is None:
            data.append({'date': start.strftime('%Y-%m-%d'), 'NDVI': None, 'NDMI': None, 'BSI': None, 'SOCI': None})
            continue
        
        point = ee.Geometry.Point(lon, lat)
        result = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point.buffer(30),
            scale=30
        ).getInfo()
        
        filtered_result = {
            'date': start.strftime('%Y-%m-%d'),
            'NDVI': result.get('NDVI'),
            'NDMI': result.get('NDMI'),
            'BSI': result.get('BSI'),
            'SOCI': result.get('SOCI')
        }
        
        data.append(filtered_result)
    
    df = pd.DataFrame(data)

    stats = {f'{index}_mean': df[index].mean() for index in ['NDVI', 'NDMI', 'BSI', 'SOCI']}
    
    return df, stats

# Streamlit app for user input and data fetching
st.title("SOC predictor using dynamically retrieved satellite image indices")

lat = st.number_input("Latitude", format="%.6f", value=54.8599)
lon = st.number_input("Longitude", format="%.6f", value=8.4114)
elevation = st.number_input("Elevation (meters)", format="%.1f", value=50.0, help="Enter elevation if known to avoid retrieval errors.")

# Soil composition inputs
sand = st.number_input("Sand percentage", min_value=0, max_value=100, step=1)
silt = st.number_input("Silt percentage", min_value=0, max_value=100, step=1)
clay = st.number_input("Clay percentage", min_value=0, max_value=100, step=1)

# Validate that percentages add up to 100
if sand + silt + clay != 100:
    st.warning("Sand, silt, and clay percentages must add up to 100%.")
else:
    # Dropdown options for categorical columns
    main_vegetation_type_values = list(freq_encoding.keys())
    land_cover_type_values = ["Cropland", "Grassland", "Woodland", "Bareland", "Shrubland"]  # Replace with actual land cover options
    
    selected_main_vegetation_type = st.selectbox("Select Main Vegetation Type", options=main_vegetation_type_values)
    selected_land_cover_type = st.selectbox("Select Land Cover Type", options=land_cover_type_values)
    
    if st.button("Fetch Data and Predict"):
        df, index_stats = fetch_quarterly_simple_indices(lat, lon)
        
        if not df.empty:
            st.success("Data fetched successfully!")
            
            # Prepare data for the model prediction
            model_input_data = {
                'lat': lat,  # Add latitude
                'long': lon, 
                'elevation': elevation,
                'sand': sand,
                'silt': silt,
                'clay': clay,
                **index_stats
            }
            
            # Apply frequency and target encodings for main_vegetation_type
            model_input_data['main_vegetation_type_freq_encoded'] = freq_encoding.get(selected_main_vegetation_type, 0)
            model_input_data['main_vegetation_type_target_encoded'] = mean_encoding.get(selected_main_vegetation_type, 0)
            
            # One-hot encode land_cover_type
            for cover_type in land_cover_type_values:
                model_input_data[f'land_cover_type_{cover_type}'] = int(selected_land_cover_type == cover_type)
            
            # Convert to DataFrame for prediction
            input_df = pd.DataFrame([model_input_data])
            # Predict and round the output to two decimal places
            prediction = round(model.predict(input_df)[0], 2)

            # Display the result with a percentage symbol
            st.write("SOC Prediction:", prediction, "%")
