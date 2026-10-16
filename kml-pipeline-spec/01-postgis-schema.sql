-- ============================================================
-- PostGIS Spatial Infrastructure
-- Field-to-gate application · WGS 84 (EPSG:4326)
-- PROPOSED ARCHITECTURE — not deployed
-- ============================================================

-- 1. Enable the PostGIS extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Create the farm polygons table with WGS 84 (EPSG:4326) spatial data type
CREATE TABLE registered_farms (
    field_id SERIAL PRIMARY KEY,
    field_name VARCHAR(100) NOT NULL,
    field_polygon_hash VARCHAR(64) UNIQUE NOT NULL,
    geom GEOMETRY(Polygon, 4326),
    verified_acreage NUMERIC(10, 2)
);

-- 3. Create a spatial index using GiST for high-performance boundary lookups
CREATE INDEX idx_registered_farms_geom
ON registered_farms
USING GIST (geom);

-- 4. Spatial lookup query to check if a new polygon intersects
--    with any existing registered fields.
--    Replace ST_GeomFromText with the incoming sanitized polygon
--    WKT or GeoJSON conversion.
SELECT field_id, field_name
FROM registered_farms
WHERE ST_Intersects(
    geom,
    ST_GeomFromText('POLYGON((-86.234561 35.123456, -86.234123 35.123890, -86.234987 35.124123, -86.234561 35.123456))', 4326)
);
