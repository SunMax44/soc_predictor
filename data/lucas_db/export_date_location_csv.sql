CREATE TABLE date_location_lucas_ag AS
SELECT "SURVEY_DATE" AS "sample_date", "TH_LAT" AS "lat", "TH_LONG" AS "long"
FROM lucas_main
WHERE "LU1_Desc" = 'Agriculture (excluding fallow land and kitchen gardens)'
ORDER BY "SURVEY_DATE" DESC;

COPY date_location_lucas_ag TO '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/date_location_lucas_ag.csv' DELIMITER ',' CSV HEADER;

