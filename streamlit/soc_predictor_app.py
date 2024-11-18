import streamlit as st

# Streamlit Page Configuration
st.set_page_config(page_title="SOC Predictor", layout="wide")

# Add custom CSS
st.markdown("""
    <style>
        /* Change the overall background color */
        .stApp {
            background-color: #f5f2e3; /* Soft Yellow */
        }

        /* Change text color throughout the app */
        div[data-testid="stMarkdownContainer"] {
            color: #4b371c; /* Soil Brown */
        }
        .stTextInput, .stNumberInput, .stSelectbox {
            color: #4b371c; /* Soil Brown for Input Text */
        }

        /* Style the sidebar */
        section[data-testid="stSidebar"] {
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

# App Title
st.title("🌾 Soil Organic Carbon Predictor")

# Sidebar
with st.sidebar:
    st.header("Input Details")
    lat = st.number_input("Latitude", format="%.6f", value=54.8599)
    lon = st.number_input("Longitude", format="%.6f", value=8.4114)

# Main Area
st.write("Enter your details in the sidebar.")
