SELECT *
FROM lucas_main_ag_model;

CREATE TABLE lucas_soil_type (
    lat DOUBLE PRECISION,
    long DOUBLE PRECISION,
    sand DOUBLE PRECISION,
	silt DOUBLE PRECISION,
	clay DOUBLE PRECISION
);

COPY lucas_soil_type (lat, long, sand, silt, clay)
FROM '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/lucas_soil_types.csv'
WITH (FORMAT csv, HEADER, DELIMITER ',');

CREATE TABLE satellite_indices (
    "lat" DOUBLE PRECISION,
    "long" DOUBLE PRECISION,
    "NDVI_mean" DOUBLE PRECISION,
    "NDVI_std" DOUBLE PRECISION,
    "NDVI_trend" DOUBLE PRECISION,
    "NDMI_mean" DOUBLE PRECISION,
    "NDMI_std" DOUBLE PRECISION,
    "NDMI_trend" DOUBLE PRECISION,
    "BSI_mean" DOUBLE PRECISION,
    "BSI_std" DOUBLE PRECISION,
    "BSI_trend" DOUBLE PRECISION,
    "SOCI_mean" DOUBLE PRECISION,
    "SOCI_std" DOUBLE PRECISION,
    "SOCI_trend" DOUBLE PRECISION
);

COPY satellite_indices (
    "lat",
    "long",
    "NDVI_mean",
    "NDVI_std",
    "NDVI_trend",
    "NDMI_mean",
    "NDMI_std",
    "NDMI_trend",
    "BSI_mean",
    "BSI_std",
    "BSI_trend",
    "SOCI_mean",
    "SOCI_std",
    "SOCI_trend"
)
FROM '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/satellite_data/landsat_indices_agged.csv'
WITH (FORMAT csv, HEADER, DELIMITER ',');

CREATE TABLE mean_temp_2017 (
	lat DOUBLE PRECISION,
	long DOUBLE PRECISION,
	mean_temp_2017 DOUBLE PRECISION);

COPY mean_temp_2017 (lat, long, mean_temp_2017)
FROM '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/satellite_data/climate/mean_temp_2017.csv'
WITH (FORMAT csv, HEADER, DELIMITER ',');

SELECT *
FROM lucas_main;

SELECT *
FROM lucas_main;

CREATE TABLE soc AS
SELECT "OC" AS SOC_in_percent,"TH_LAT" AS lat, "TH_LONG" AS long
FROM lucas_main
WHERE "LU1_Desc" = 'Agriculture (excluding fallow land and kitchen gardens)';

SELECT *
FROM lucas_main_ag_model;

-- Creating the main table with columns from all other tables
CREATE TABLE feature_table AS
SELECT 
    a.sample_date,
	ROUND(a.lat::NUMERIC, 5) AS lat,
    ROUND(a.long::NUMERIC, 5) AS long,
	a.depth,
	a.elevation,
    t.mean_temp_2017,
    ind."NDVI_mean",
	ind."NDVI_std",
	ind."NDVI_trend",
	ind."NDMI_mean",
	ind."NDMI_std",
	ind."NDMI_trend",
	ind."BSI_mean",
	ind."BSI_std",
	ind."BSI_trend",
	ind."SOCI_mean",
	ind."SOCI_std",
	ind."SOCI_trend",
	a.land_cover_type,
	a.main_vegetation_type,
	s.SOC_in_percent
FROM 
    lucas_main_ag_model AS a
LEFT JOIN 
    mean_temp_2017 AS t ON ROUND(a.lat::NUMERIC, 5) = ROUND(t."lat"::NUMERIC, 5) AND ROUND(a.long::NUMERIC, 5) = ROUND(t."long"::NUMERIC, 5)
LEFT JOIN 
    satellite_indices AS ind ON ROUND(a.lat::NUMERIC, 5) = ROUND(ind.lat::NUMERIC, 5) AND ROUND(a.long::NUMERIC, 5) = ROUND(ind.long::NUMERIC, 5)
LEFT JOIN 
    soc AS s ON ROUND(a.lat::NUMERIC, 5) = ROUND(s.lat::NUMERIC, 5) AND ROUND(a.long::NUMERIC, 5) = ROUND(s.long::NUMERIC, 5)
ORDER BY lat Desc;

UPDATE feature_table
SET soc_in_percent = soc_in_percent / 10;

SELECT *
FROM mean_temp_2017;

CREATE TABLE final_feature_table AS(
SELECT feature_table.*, st.sand, st.silt, st.clay
FROM feature_table
LEFT JOIN
	lucas_soil_type AS st ON feature_table.lat = ROUND(st.lat::NUMERIC, 5) AND feature_table.long = ROUND(st.long::NUMERIC, 5));

SELECT *
FROM feature_table
ORDER BY lat DESC;

SELECT *
FROM lucas_soil_type
ORDER BY lucas_soil_type.long Asc;

COPY final_feature_table TO '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/feature_table.csv' WITH (FORMAT csv, HEADER);