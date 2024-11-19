# SOC Predictor

### Project Scope

This project focuses on predicting **field level** **soil organic carbon (SOC)** levels across **Europe** to contribute to current efficiency vs. effectiveness tradeoffs by making SOC modeling both more efficient and effective.


Already implemented:
- Europe-wide SOC modelling
- EU Lucas 2018 soil sample dataset with location-specific features (soil type, elevation, land use & cover) as well as the model's target (SOC)
- Landsat-8 OLI data (bands 2-6) to derive indices for vegetation, moisture, bare soil and soil organic carbon (NDVI, NDMI, BSI, SOCI)
- LightGBM model was chosen for its better performance (e.g. over RandomForest, XGBoost, etc.)
- Hyperparameter Tuning
- MSE: 1.94
- R^2 Score: 0.476

Next steps:
- Model evaluation with different soil sampling data
- Implementation of climate data (temperature & precipitation) additional features
- Add models to predict other soil properties (e.g. bulk density or cation exchange capacity): Connecting the current feature dataset to soilgrids using SOC and other features


### Background
By modeling SOC in relation to **land use type, crop health, and location**, the project aims to inform sustainable land management practices that can enhance carbon sequestration in soils, thereby yielding positive aspects such as **increasing soil fertility, reducing atmospheric CO₂ levels and increasing soil water retention**. With soils being a significant carbon sink, accurately estimating SOC levels is essential for climate action.

### Key Objectives

1. **SOC Prediction**: Provide SOC predictions that can inform carbon sequestration strategies across diverse landscapes.
2. **Impact of Agricultural Production Types**: Incorporate multi-year environmental data to track SOC changes and assess the effectiveness of land management practices.
3. **Database Integration**: Use PostGIS to organize and manage spatial and temporal data effectively, facilitating SOC retrieval and analysis.
4. **Visualization**: Offer tools to visualize SOC distribution and trends, enabling users to make informed decisions.

### Initial Outline & Key Steps

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
  

### Key challenges

### Data Sources

Used:
-- **LUCAS DB**
     - EU Lucas 2018 soil sample Database's 10971 agricultural soil data
     - Access: https://esdac.jrc.ec.europa.eu/projects/lucas
  
-- **Landsat Data**
     - Accessed via Google Earth Engine
     - The following indices were calculated using the specific bands of the 10971 GPS locations of the Lucas sample dataset:
        NRVI (Normalized Red-Edge Vegetation Index)
        NRDE (Normalized Red-Edge Difference Index)
        BI (Bare Soil Index)
        SOCI (Soil Organic Carbon Index)
  
To be used:
-- **SoilGrids**
     - Data already retrieved for all German grids (250m resolution)
     - Access:  
        https://soilgrids.org/ (UI)
        https://files.isric.org/soilgrids/latest/data/ (files)
-- **Bodenzustandserhebung (BZE) by Thünen Institute**
   - The datasets were unsuitable for location-specific features, as locations are randomly distributed within a 4 km radius for      privacy.
   - Access: https://www.openagrar.de/receive/openagrar_mods_0005487
-- **Climate data**
     - retrieve mean temperature and precipitation over the past years for train_set and input locations
     - e.g. through Google Earth Engine


### Feature List (to completed)
-Land Use Type
-Land Cover Type
-NRVI (Normalized Red-Edge Vegetation Index)
-EVI (Enhanced Vegetation Index)
-NRDE (Normalized Red-Edge Difference Index)
-BI (Bare Soil Index)
-SOCI (Soil Organic Carbon Index)

## Usage

1. **Data Preparation**: Run preprocessing scripts to standardize data formats.
2. **Training the Model**: Train the model on historical data and validate with recent records.
3. **Running Predictions**: Use the Streamlit app or scripts to generate predictions for selected regions and timeframes.
