import streamlit as st

st.set_page_config(page_title="SOC Predictor", layout="wide")
st.title("SOC Predictor")

import json
import ee

# Initialize Earth Engine with service account credentials
GEE_CREDENTIALS = json.loads(st.secrets["GEE_CREDENTIALS_JSON"])

# Write the JSON to a temporary file
with open("temp-gee-key.json", "w") as key_file:
    json.dump(GEE_CREDENTIALS, key_file)

EE_CREDENTIALS = ee.ServiceAccountCredentials(GEE_CREDENTIALS["client_email"], "temp-gee-key.json")
ee.Initialize(EE_CREDENTIALS)


# Add basic inputs
lat = st.number_input("Latitude", format="%.6f", value=54.8599)
lon = st.number_input("Longitude", format="%.6f", value=8.4114)

st.write("Enter your latitude and longitude above.")

with st.sidebar:
    st.header("Input Details")
    st.number_input("Elevation (meters)", format="%.1f", value=50.0)

# Dropdowns for Vegetation and Land Cover
main_vegetation_type_values = ["Forest", "Grassland", "Cropland"]  # Example values
land_cover_type_values = ["Shrubland", "Bareland", "Woodland"]

selected_main_vegetation_type = st.selectbox(
    "Select Main Vegetation Type", options=main_vegetation_type_values
)
selected_land_cover_type = st.selectbox(
    "Select Land Cover Type", options=land_cover_type_values
)

# Validation for Sand, Silt, and Clay
sand = st.number_input("Sand (%)", min_value=0, max_value=100, step=1)
silt = st.number_input("Silt (%)", min_value=0, max_value=100, step=1)
clay = st.number_input("Clay (%)", min_value=0, max_value=100, step=1)

if sand + silt + clay != 100:
    st.warning("Sand, silt, and clay percentages must add up to 100%.")
else:
    st.success("Valid soil composition!")


