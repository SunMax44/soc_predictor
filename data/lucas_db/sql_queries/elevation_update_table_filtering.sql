-- Create a temporary table for the CSV data
CREATE TEMP TABLE temp_csv_data (
    date DATE,
	lat DOUBLE PRECISION,
	long DOUBLE PRECISION,
    elevation INTEGER  -- Replace TYPE with the actual data type of your new column
);

-- Copy data from the CSV into the temporary table
COPY temp_csv_data(date, lat, long, elevation)
FROM '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation_fixed.csv'
DELIMITER ','  -- Specify the delimiter used in your CSV
CSV HEADER;    -- Use this if your CSV has a header row

-- Update the main table using data from the temporary table based on both latitude and longitude
UPDATE lucas_main
SET "Elev" = temp_csv_data.elevation
FROM temp_csv_data
WHERE lucas_main."TH_LAT" = temp_csv_data.lat
  AND lucas_main."TH_LONG" = temp_csv_data.long;

SELECT *
FROM lucas_main;

SELECT * FROM temp_csv_data LIMIT 10;

COMMIT;

SELECT lucas_main."TH_LAT", lucas_main."TH_LONG", lucas_main."Elev", temp_csv_data.elevation
FROM lucas_main
JOIN temp_csv_data
ON lucas_main."TH_LAT" = temp_csv_data.lat
   AND lucas_main."TH_LONG" = temp_csv_data.long
LIMIT 10;

UPDATE TABLE lucas_main AS
SELECT *
FROM lucas_main
WHERE "LU1_Desc" = 'Agriculture (excluding fallow land and kitchen gardens)'
ORDER BY "SURVEY_DATE" DESC;

CREATE TABLE lucas_main_ag_model AS
SELECT "SURVEY_DATE" AS sample_date, "TH_LAT" as lat, "TH_LONG" AS long, "Depth" as "depth", "Elev" AS elevation, "LC0_Desc" AS land_cover_type, "LC1_Desc" AS main_vegetation_type 
FROM lucas_main_agriculture
WHERE "LU1_Desc" = 'Agriculture (excluding fallow land and kitchen gardens)'
ORDER BY "SURVEY_DATE" DESC;

SELECT *
FROM lucas_main_ag_model