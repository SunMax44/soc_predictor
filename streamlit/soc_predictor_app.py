import streamlit as st
import pandas as pd
import numpy as np
import ee
import pickle
from datetime import datetime, timedelta
import json

# Streamlit Page Configuration
st.set_page_config(
    page_title="SOC Predictor",
    page_icon="🌾",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
        /* Main App Background (Dark Brown) */
        .stApp {
            background-color: #4a2c2a; /* Chocolate Brown */
            color: #e0d4b4; /* Sidebar Font Color for Main Text */
        }

        /* Sidebar Background (Light Brown) */
        section[data-testid="stSidebar"] {
            background-color: #e0d4b4; /* Light Brown */
        }

        /* Buttons (Green) */
        .stButton>button {
            background-color: #81c784; /* Green */
            color: white;
            border-radius: 10px;
            font-weight: bold;
            padding: 10px 20px;
        }
        .stButton>button:hover {
            background-color: #66bb6a; /* Darker Green */
        }

        /* Input Field Text Color */
        .stTextInput, .stNumberInput, .stSelectbox {
            color: #e0d4b4; /* Sidebar Font Color */
        }

        /* Header and Markdown Text */
        div[data-testid="stMarkdownContainer"] {
            color: #e0d4b4; /* Sidebar Font Color */
        }
    </style>
""", unsafe_allow_html=True)

# App Title
st.title("🌾 Soil Organic Carbon Predictor")

# Sidebar Inputs
with st.sidebar:
    st.header("Input Details")
    lat = st.number_input("Latitude", format="%.6f", value=54.8599)
    lon = st.number_input("Longitude", format="%.6f", value=8.4114)
    elevation = st.number_input("Elevation (meters)", format="%.1f", value=50.0, help="Enter elevation if known.")
    sand = st.number_input("Sand (%)", min_value=0, max_value=100, step=1)
    silt = st.number_input("Silt (%)", min_value=0, max_value=100, step=1)
    clay = st.number_input("Clay (%)", min_value=0, max_value=100, step=1)

    # Validation
    if sand + silt + clay != 100:
        st.warning("⚠️ Sand, silt, and clay percentages must total 100%.")
    else:
        st.success("Valid soil composition!")

# Dropdown Inputs for Vegetation and Land Cover
main_vegetation_type_values = ["Forest", "Grassland", "Cropland"]
land_cover_type_values = ["Shrubland", "Bareland", "Woodland"]
selected_main_vegetation_type = st.selectbox("Select Main Vegetation Type", options=main_vegetation_type_values)
selected_land_cover_type = st.selectbox("Select Land Cover Type", options=land_cover_type_values)

# Earth Engine Initialization
GEE_CREDENTIALS = json.loads(st.secrets["GEE_CREDENTIALS_JSON"])
with open("temp-gee-key.json", "w") as key_file:
    json.dump(GEE_CREDENTIALS, key_file)
EE_CREDENTIALS = ee.ServiceAccountCredentials(GEE_CREDENTIALS["client_email"], "temp-gee-key.json")
ee.Initialize(EE_CREDENTIALS)

# Load Model
with open("ml_model/tuned_lightgbm_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

# Function to Fetch Indices
def fetch_quarterly_simple_indices(lat, lon):
    # Example simplified data for testing
    return {"NDVI_mean": 0.5, "NDMI_mean": 0.3, "BSI_mean": -0.2, "SOCI_mean": 0.1}

# Predict Button
if st.button("Fetch Data and Predict"):
    # Fetch indices
    stats = fetch_quarterly_simple_indices(lat, lon)

    # Prepare model input
    model_input_data = {
        "lat": lat,
        "long": lon,
        "elevation": elevation,
        "sand": sand,
        "silt": silt,
        "clay": clay,
        **stats,
    }
    # Example encoding
    model_input_data["main_vegetation_type_encoded"] = 0  # Mock encoding
    model_input_data["land_cover_type_encoded"] = 1  # Mock encoding

    # Convert to DataFrame for prediction
    input_df = pd.DataFrame([model_input_data])

    # Perform prediction
    prediction = model.predict(input_df)[0]
    st.success(f"Predicted SOC: {prediction:.2f}%")
