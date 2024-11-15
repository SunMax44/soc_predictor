SELECT "Elev" AS elevation, "LC0_Desc" AS land_cover_type, "LU1_Desc" AS land_use_type, "LC1_Desc" AS land_cover_detail
FROM lucas_main;

SELECT *
FROM lucas_main
WHERE "LC0_Desc" = 'Wetlands';