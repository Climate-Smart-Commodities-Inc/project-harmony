# KML Pipeline Spec — Field-to-Gate Tracking
**Status:** PROPOSED ARCHITECTURE — not deployed. No database exists, no endpoint is live, no farmer has uploaded anything.
**Assembled:** 2026-10-16 from Harmony's AI-generated spec session.

## Architecture

```
[HTML5 Portal / Drag & Drop]          → 02-upload-portal.html
            ↓  (GeoJSON Upload)
[Flask Gateway]                       → 03-flask-api.py
   ── (Shapely Engine: validates no overlaps / self-intersections)
            ↓  (Passes Validation)
[Data Pipeline Hasher]                → generate_polygon_hash() in 03
   ── (0x-prefixed bytes32 coordinate hash)
            ↓
[Advanced Validation]                 → 07-validation-pipeline.py
   ── (MultiPolygon support, exact intersection logging, RSA telemetry signatures)
            ↓
[IoT Scale House Gate]                → 04-hmac-verification.py
   ── (HMAC-SHA256 payload verification, constant-time compare)
            ↓
[LCA Calculation Engine]              → 05-lca-calculator.py
   ── (biomass density × factor, ×1000 fixed precision → uint32)
            ↓
[Smart Contract State]                → (not built)
   ── (P2P asset payout to regional producer)
```

## Smart Contract Parameters (cradle-to-gate)

| Parameter | Type | Source |
|---|---|---|
| `field_polygon_hash` | bytes32 | SHA-256 of exact spatial coordinates |
| `verified_acreage` | uint32 | ST_Area on validated KML |
| `raw_biomass_mass` | uint64 | Certified scale-house gate, kg |
| `moisture_content_pct` | uint8 | Probe reading, scaled (85 = 8.5%) |
| `cradle_to_gate_lca_metric` | uint32 | Net CO₂e per functional unit, ×1000 |
| `metal_accumulator_status` | bool | Lab heavy-metal clearance flag |

The `metal_accumulator_status` flag encodes Harmony's two-stream guard: contaminated-site biomass never becomes feedstock without lab clearance.

## Files

| File | Contents |
|---|---|
| `01-postgis-schema.sql` | PostGIS extension, `registered_farms` table (EPSG:4326), GiST index, ST_Intersects lookup |
| `02-upload-portal.html` | Farmer-facing drag-and-drop KML/GeoJSON upload form |
| `03-flask-api.py` | `/api/register-field` endpoint: ingest, Shapely validation, logging, polygon hash |
| `04-hmac-verification.py` | `verify_scale_house_payload()` — HMAC-SHA256 scale-house auth |
| `05-lca-calculator.py` | `calculate_cradle_to_gate_lca()` — biomass × acreage × factor |
| `06-pytest-suite.py` | Tests: valid polygon, self-intersection rejection, missing file |
| `07-validation-pipeline.py` | `validate_and_process_payload()` — MultiPolygon, RSA signatures, versioning hash |

## Spatial standards

- CRS: EPSG:4326 (WGS 84) for all raw KML; reproject drone state-plane data before parsing.
- One `<Polygon>` per farm plot: outer boundary + ExtendedData (soil type, prior yield).
- Self-intersection check on ingest; overlap rejection against registered neighbors via PostGIS `ST_Intersects`.
- Versioning: historical polygons are never modified — superseded rows flip to `HISTORICAL`, new rows carry updated hashes.

## Source spec documents

- Google Doc "KML:PolygonRenderingTechSpecs" (Harmony's drive)
- `workspace/user/files/KML_PolygonRenderingTechSpecs_47_1bgj.pdf`
- Gmail drafts 2026-10-16 ~17:25 CDT (AI session outputs archived as drafts)

## Next technical steps (when Harmony says go)

1. Choose the GitHub repo (`project-harmony` is the natural home — MRV code already lives there).
2. Commit this spec as v0.1 tagged PROPOSED ARCHITECTURE.
3. Stand up PostGIS locally; run `01-postgis-schema.sql`.
4. Wire `02` → `03` → `04`/`05` end to end with a test polygon before any farmer-facing claim.
