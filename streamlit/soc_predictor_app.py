import streamlit as st
import pandas as pd
import numpy as np
import ee
import pickle
from datetime import datetime, timedelta
import os
import json

# Streamlit Page Configuration
st.set_page_config(
    page_title="SOC Predictor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for Custom Design
st.markdown("""
    <style>
        /* Background and Font Colors */
        body {
            background-color: #f5f2e3;  /* Soft Yellow */
            color: #4b371c;  /* Soil Brown */
        }
        header {
            background-color: #81c784;  /* Light Green for Header */
        }
        .stButton>button {
            background-color: #f7c800;  /* Corn Yellow for Button */
            color: #4b371c;  /* Soil Brown Text for Buttons */
            border-radius: 10px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #f9e600;  /* Lighter Yellow for Hover */
        }
        .stSidebar {
            background-color: #e0d4b4;  /* Soft Brown for Sidebar */
        }
        .stNumberInput label, .stSelectbox label {
            font-weight: bold;
            color: #4b371c;  /* Soil Brown for Labels */
        }
    </style>
""", unsafe_allow_html=True)

# App Title with Icon
st.title("🌾 Soil Organic Carbon Predictor")

# Initialize Earth Engine with service account credentials
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
freq_encoding = np.load("streamlit/main_vegetation_type_freq_encoding.npy", allow_pickle=True).item()
mean_encoding = np.load("streamlit/main_vegetation_type_mean_encoding.npy", allow_pickle=True).item()

# Function to mask clouds in Landsat images
def mask_clouds_landsat(image):
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 5).eq(0).And(qa.bitwiseAnd(1 << 3).eq(0))
    return image.updateMask(cloud_mask)

# Function to calculate NDVI, NDMI, BSI, and SOCI
def calculate_indices_landsat(image):
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    ndmi = image.normalizedDifference(['SR_B5', 'SR_B6']).rename('NDMI')
    bsi
