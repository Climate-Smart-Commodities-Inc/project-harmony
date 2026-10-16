"""
Advanced validation pipeline — MultiPolygon support, exact intersection
logging, RSA telemetry signature verification, versioning hash.
PROPOSED ARCHITECTURE — not deployed.
"""
import json
import logging
import hashlib
from typing import Dict, Any, List, Optional
import shapely.geometry
import shapely.validation
from shapely.ops import unary_union
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

# Configure logging to assist farmers with localized boundary troubleshooting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SecurityError(Exception):
    pass


def validate_and_process_payload(
    incoming_payload: Dict[str, Any],
    existing_network_polygons: List[Dict[str, Any]],
    station_public_key: Optional[RSAPublicKey] = None
) -> Dict[str, Any]:
    """
    Validates MultiPolygon configurations, prints exact geographic error locations,
    and checks IoT device signatures to guarantee data authenticity.
    """
    # --- STEP 1: CRYPTOGRAPHIC VERIFICATION ---
    if station_public_key and "signature" in incoming_payload:
        raw_data = json.dumps(incoming_payload["data"], sort_keys=True).encode('utf-8')
        signature = bytes.fromhex(incoming_payload["signature"])
        try:
            station_public_key.verify(
                signature,
                raw_data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            logging.info("Cryptographic Verification Passed: Inbound telemetry payload is authentic.")
        except InvalidSignature:
            logging.error("Security Alert: Unauthorized modification detected on telemetry stream.")
            raise SecurityError("Telemetry payload failed cryptographic signature check.")

    # --- STEP 2: MULTI-POLYGON SUPPORT & STRUCTURAL INTEGRITY ---
    geom_data = incoming_payload["data"]["geometry"]
    input_shape = shapely.geometry.shape(geom_data)

    if not isinstance(input_shape, (shapely.geometry.Polygon, shapely.geometry.MultiPolygon)):
        raise TypeError("Spatial Resolution Error: Shape must be a valid Polygon or MultiPolygon.")

    # Check for self-intersections (e.g., looping drone paths or bad coordinate ordering)
    if not input_shape.is_valid:
        # Locate the exact node geometry causing structural invalidity
        invalid_nodes = shapely.validation.explain_validity(input_shape)
        logging.error(f"Geospatial Error: Self-intersecting lines found. Node details: {invalid_nodes}")
        return {
            "status": "FAILED",
            "reason": "Self-intersection",
            "intersection_coordinates": str(invalid_nodes)
        }

    # --- STEP 3: BOUNDARY OVERLAP ERROR HANDLING & LOGGING ---
    network_shapes = []
    for entry in existing_network_polygons:
        network_shapes.append(shapely.geometry.shape(entry["geometry"]))

    if network_shapes:
        combined_network = unary_union(network_shapes)
        if input_shape.intersects(combined_network):
            # Isolate the exact crossing paths or common overlap regions
            overlap_geometry = input_shape.intersection(combined_network)
            overlap_coords = list(overlap_geometry.bounds)  # [minx, miny, maxx, maxy]
            logging.warning(f"Contract Conflict: Boundary overlap with neighboring parcel near bounds: {overlap_coords}")
            return {
                "status": "CONFLICT",
                "reason": "Boundary Overlap",
                "conflict_bounds": overlap_coords,
                "overlap_wkt": overlap_geometry.wkt
            }

    # --- STEP 4: VERSIONING HASH GENERATION ---
    # Explicit hash of the coordinates to track changes across crop cycles
    coord_string = json.dumps(geom_data, sort_keys=True)
    coordinate_hash = hashlib.sha256(coord_string.encode('utf-8')).hexdigest()

    logging.info(f"Field Validation Successful. Area calculated: {input_shape.area:.2f} sq units.")
    return {
        "status": "VALIDATED",
        "calculated_area": input_shape.area,
        "coordinate_hash": coordinate_hash
    }
