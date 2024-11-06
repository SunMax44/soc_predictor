# Humus Predictor

This project focuses on predicting **soil organic carbon (SOC)** levels across **Germany** to contribute to current efficiency vs. effectiveness tradeoffs by making SOC modeling both more efficient and effective. By modeling SOC in relation to **land use type, crop health, and location**, the project aims to inform sustainable land management practices that can enhance carbon sequestration in soils, thereby yielding positive aspects such as **increasing soil fertility, reducing atmospheric CO₂ levels and increasing soil water retention**. With soils being a significant carbon sink, accurately estimating SOC levels is essential for climate action. This project uses various land use, crop type, and soil health indicators to model SOC levels and examine changes over time using Machine Learning algorithm.

### Key Objectives

1. **SOC Prediction**: Provide SOC predictions that can inform carbon sequestration strategies across diverse landscapes.
2. **Impact of Agricultural Production Types**: Incorporate multi-year environmental data to track SOC changes and assess the effectiveness of land management practices.
3. **Database Integration**: Use PostGIS to organize and manage spatial and temporal data effectively, facilitating SOC retrieval and analysis.
4. **Visualization**: Offer tools to visualize SOC distribution and trends, enabling users to make informed decisions.

## Outline & Key Steps

1. **Data Integration**  
   - Aggregate SOC variables, land use types, and crop health indicators from multiple data sources.
   - Major data sources include:
     - **SoilGrids**: Provides SOC and related soil property data by Wageningen University.
     - **LUCAS DB (Land Use/Cover Area frame statistical Survey)**: Offers harmonized soil and land use data across Europe provided by a joint research centre by the European Commission.
     - **Bodenzustandserhebung (BZE)**: Supplies in-depth soil condition data for Germany by the German Thünen agricultural resarch institute.
     - **Sentinel-2 Data**: Adds geospatial analysis capabilities for environmental and land cover data accessed by Google Earth Data.
    
2. **Spatial Database**  
   - Employ **PostGIS** to store and manage SOC data efficiently.
   - Enable spatial and temporal filtering for targeted SOC queries.

3. **Data Preprocessing**  
   - Standardize input features, including grid sizes, to ensure compatibility.
   - Handle temporal data for effective trend analysis.

4. **Model Development**  
   - Train and validate machine learning models (e.g., Random Forest, Decision Tree) on multi-year data.
   - Utilize Principal Component Analysis (PCA) to optimize feature dimensionality.

5. **Streamlit Web App**  
   - Develop an interactive web app for SOC prediction and visualization.
   - Allow users to explore SOC data by region, land use type, and timeframe.

## Data Sources

- **SoilGrids**
  https://soilgrids.org/ (UI)
  https://files.isric.org/soilgrids/latest/data/ (files)
- **LUCAS DB**
  https://esdac.jrc.ec.europa.eu/projects/lucas
- **Bodenzustandserhebung (BZE) by Thünen Institute**
  https://www.openagrar.de/receive/openagrar_mods_00054877
- **Google Earth Engine**
  Germany data for calculating:
  NRVI (Normalized Red-Edge Vegetation Index)
  NRDE (Normalized Red-Edge Difference Index)
  BI (Bare Soil Index)


## Possible Features
Soil Organic Carbon (SOC)
Soil pH
Soil Texture (sand, silt, clay proportions)
Bulk Density
Carbon/Nitrogen Ratio
Nutrient Levels (e.g., nitrogen, phosphorus, potassium)
Land Use Type
Land Cover
Elevation and Slope
Soil Depth
Soil Moisture
Soil Carbon Content by Depth Layers
Climate Zone
Land Management Practices (e.g., crop rotation, tillage)
Soil Erosion Rates
Cation Exchange Capacity (CEC)
Available Water Content
Temperature (mean, minimum, maximum)
Precipitation (total, seasonal)
Solar Radiation
Evapotranspiration
Land Cover Type Change
Crop Type and Health
NRVI (Normalized Red-Edge Vegetation Index)
EVI (Enhanced Vegetation Index)
NRDE (Normalized Red-Edge Difference Index)
BI (Bare Soil Index)

## Usage

1. **Data Preparation**: Run preprocessing scripts to standardize data formats.
2. **Training the Model**: Train the model on historical data and validate with recent records.
3. **Running Predictions**: Use the Streamlit app or scripts to generate predictions for selected regions and timeframes.
