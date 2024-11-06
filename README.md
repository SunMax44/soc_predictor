# Soil Organic Carbon (SOC) Prediction Model

This project focuses on predicting soil organic carbon (SOC) levels across Germany to contribute to climate change mitigation efforts. By modeling SOC in relation to land use type, crop health, and location, the project aims to inform sustainable land management practices that can enhance carbon sequestration in soils, thereby reducing atmospheric CO₂ levels. Monitoring SOC also provides insights into soil health trends across different regions, supporting the long-term resilience of agricultural landscapes.

## Project Overview

With soils being a significant carbon sink, accurately estimating SOC levels is essential for climate action. This project uses various land use, crop type, and soil health indicators to model SOC levels and examine changes over time. A primary focus is on assessing the role of soils in climate change mitigation, with a secondary emphasis on soil health monitoring.

### Key Objectives

1. **Climate Change Mitigation**: Provide SOC predictions that can inform carbon sequestration strategies across diverse landscapes.
2. **Trend Analysis**: Incorporate multi-year environmental data to track SOC changes and assess the effectiveness of land management practices.
3. **Database Integration**: Use PostGIS to organize and manage spatial and temporal data effectively, facilitating SOC retrieval and analysis.
4. **Visualization**: Offer tools to visualize SOC distribution and trends, enabling users to make informed decisions.

## Features

1. **Data Integration**  
   - Aggregate SOC variables, land use types, and crop health indicators from multiple data sources.
   - Major data sources include:
     - **SoilGrids**: Provides SOC and related soil property data.
     - **LUCAS DB (Land Use/Cover Area frame statistical Survey)**: Offers harmonized soil and land use data across Europe.
     - **Bodenzustandserhebung (BZE)**: Supplies in-depth soil condition data for Germany.
     - **Google Earth Engine**: Adds geospatial analysis capabilities for environmental and land cover data.

2. **Data Preprocessing**  
   - Standardize input features, including grid sizes, to ensure compatibility.
   - Handle temporal data for effective trend analysis.

3. **Model Development**  
   - Train and validate machine learning models (e.g., Random Forest, Decision Tree) on multi-year data.
   - Utilize Principal Component Analysis (PCA) to optimize feature dimensionality.

4. **Spatial Database**  
   - Employ PostGIS to store and manage SOC data efficiently.
   - Enable spatial and temporal filtering for targeted SOC queries.

5. **Streamlit Web App**  
   - Develop an interactive web app for SOC prediction and visualization.
   - Allow users to explore SOC data by region, land use type, and timeframe.

## Data Sources

- **SoilGrids**
- **LUCAS DB**
- **Bodenzustandserhebung (BZE)**
- **Google Earth Engine**
- **PostGIS Database**

## Usage

1. **Data Preparation**: Run preprocessing scripts to standardize data formats.
2. **Training the Model**: Train the model on historical data and validate with recent records.
3. **Running Predictions**: Use the Streamlit app or scripts to generate predictions for selected regions and timeframes.

## Future Directions

- **Feature Expansion**: Integrate additional agronomic and environmental variables, such as weather patterns and soil pH.
- **Predictive Model Refinement**: Experiment with advanced models for improved prediction accuracy.
- **Enhanced Visualization**: Create interactive SOC maps to illustrate changes over time and across land use types.
