import streamlit as st

st.set_page_config(page_title="SOC Predictor", layout="wide")
st.title("SOC Predictor")

# Add basic inputs
lat = st.number_input("Latitude", format="%.6f", value=54.8599)
lon = st.number_input("Longitude", format="%.6f", value=8.4114)

st.write("Enter your latitude and longitude above.")
