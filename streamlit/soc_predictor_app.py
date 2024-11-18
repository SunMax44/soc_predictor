import streamlit as st

st.set_page_config(page_title="SOC Predictor", layout="wide")
st.title("SOC Predictor")

st.markdown("""
    <style>
        /* Change the overall background */
        .stApp {
            background-color: #f5f2e3; /* Soft Yellow */
        }

        /* Change text color across the app */
        html, body, [class*="css"] {
            color: #4b371c; /* Soil Brown */
            font-family: "Arial", sans-serif;
        }

        /* Style the sidebar */
        .css-1d391kg { 
            background-color: #e0d4b4; /* Light Brown */
        }

        /* Style buttons */
        .stButton>button {
            background-color: #f7c800; /* Corn Yellow */
            color: #4b371c; /* Soil Brown */
            border-radius: 10px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #f9e600; /* Lighter Yellow */
        }
    </style>
""", unsafe_allow_html=True)



import json
import ee

# Initialize Earth Engine with service account credentials
GEE_CREDENTIALS = json.loads(st.secrets["GEE_CREDENTIALS_JSON"])

# Write the JSON to a temporary file
with open("temp-gee-key.json", "w") as key_file:
    json.dump(GEE_CREDENTIALS, key_file)

EE_CREDENTIALS = ee.ServiceAccountCredentials(GEE_CREDENTIALS["client_email"], "temp-gee-key.json")
ee.Initialize(EE_CREDENTIALS)

import pickle

# Load the trained model
with open("ml_model/tuned_lightgbm_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

def fetch_quarterly_simple_indices(lat, lon):
    # (Simplify the logic for now to ensure this runs)
    return {"NDVI_mean": 0.5, "NDMI_mean": 0.3, "BSI_mean": -0.2, "SOCI_mean": 0.1}


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

if st.button("Fetch Data and Predict"):
    # Fetch data (mocked for now)
    stats = fetch_quarterly_simple_indices(lat, lon)

    # Prepare input for prediction
    model_input_data = {
        "lat": lat,
        "long": lon,
        "sand": sand,
        "silt": silt,
        "clay": clay,
        **stats,
    }

    # Example encoding for dropdowns
    model_input_data["main_vegetation_type_encoded"] = 0  # Mock encoding
    model_input_data["land_cover_type_encoded"] = 1  # Mock encoding

    input_df = pd.DataFrame([model_input_data])

    # Perform prediction (mocked for now)
    prediction = model.predict(input_df)[0]
    st.success(f"Predicted SOC: {prediction:.2f}%")



