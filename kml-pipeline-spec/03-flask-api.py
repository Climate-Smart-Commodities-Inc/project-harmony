"""
Flask backend — field registration endpoint.
Ingests KML/GeoJSON uploads, validates geometry with Shapely,
generates the SHA-256 polygon hash for the smart contract payload.
PROPOSED ARCHITECTURE — not deployed.
"""
import hashlib
import json
import logging
from flask import Flask, request, jsonify
import shapely.geometry
from shapely.ops import unary_union

# Configure error logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


def generate_polygon_hash(geometry_coordinates: list) -> str:
    """
    Calculates the SHA-256 cryptographic hash of the exact spatial coordinates
    to secure the land registry data for the smart contract payload.
    """
    coord_string = json.dumps(geometry_coordinates, sort_keys=True)
    hash_object = hashlib.sha256(coord_string.encode('utf-8'))
    hex_digest = hash_object.hexdigest()
    return f"0x{hex_digest}"


@app.route('/api/register-field', methods=['POST'])
def register_field():
    if 'file' not in request.files:
        logger.warning("Upload attempt failed: No file provided in request.")
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files['file']
    field_name = request.form.get('fieldName')
    soil_type = request.form.get('soilType')

    if file.filename == '':
        logger.warning("Upload attempt failed: Empty filename.")
        return jsonify({"error": "Empty filename."}), 400

    try:
        file_content = file.read().decode('utf-8')
        geojson_data = json.loads(file_content)

        # Extract and validate geometry structure
        feature = geojson_data.get('features', [{}])[0]
        geometry = feature.get('geometry')

        if not geometry:
            raise ValueError("Missing 'geometry' object in GeoJSON feature payload.")

        input_shape = shapely.geometry.shape(geometry)

        # 1. Self-intersection check
        if not input_shape.is_valid:
            logger.error(f"Spatial Validation Failure for field '{field_name}': Self-intersecting polygon or coordinate mismatch.")
            return jsonify({"error": "Spatial Validation Failure: Invalid self-intersecting polygon or coordinate mismatch."}), 422

        calculated_area_sq_meters = input_shape.area

        # 2. Generate cryptographic polygon hash for smart contract payload
        coordinates = geometry.get('coordinates', [])
        field_polygon_hash = generate_polygon_hash(coordinates)

        logger.info(f"Successfully validated field '{field_name}' with hash {field_polygon_hash}")
        return jsonify({
            "status": "VALIDATED",
            "field_name": field_name,
            "soil_type": soil_type,
            "calculated_area_sq_m": round(calculated_area_sq_meters, 2),
            "field_polygon_hash": field_polygon_hash,
            "spatial_integrity_verified": True
        }), 200

    except json.JSONDecodeError as jde:
        logger.error(f"JSON parsing error during upload for field '{field_name}': {str(jde)}")
        return jsonify({"error": "Invalid file format. Expected valid GeoJSON."}), 400
    except (KeyError, IndexError, TypeError) as val_err:
        logger.error(f"Coordinate schema or structure mismatch error: {str(val_err)}")
        return jsonify({"error": f"Coordinate schema mismatch: {str(val_err)}"}), 422
    except Exception as e:
        logger.exception(f"Unexpected server error processing map upload for '{field_name}': {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
