COPY bze_horizon_data(PointID, HorizontID, Horizon symbol, Soil texture, Soil colour, Stones, Carbonate, Organic matter content, rooting_intensity)
FROM '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/thuenen_institute_bodenzustandserhebung/HORIZON_DATA.csv'
DELIMITER ',' 
CSV HEADER;