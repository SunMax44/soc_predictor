import streamlit as st

# Page Config
st.set_page_config(
    page_title="SOC Predictor",
    page_icon="🌾",
    layout="wide",
)

# Debug: Simple Layout
st.title("🌾 Soil Organic Carbon Predictor")

with st.sidebar:
    st.header("Input Details")
    lat = st.number_input("Latitude (°)", format="%.6f", value=54.8599)
    lon = st.number_input("Longitude (°)", format="%.6f", value=8.4114)
    st.write("This is the sidebar.")

st.write("This is the main area.")
