"""
pytest suite — polygon validation and error logging.
PROPOSED ARCHITECTURE — not deployed.
"""
import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_register_field_success(client):
    valid_geojson = {
        "features": [
            {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.234561, 35.123456],
                            [-86.234123, 35.123890],
                            [-86.234987, 35.124123],
                            [-86.234561, 35.123456]
                        ]
                    ]
                }
            }
        ]
    }

    data = {
        'fieldName': 'Test_Field_01',
        'soilType': 'Maury Silt Loam',
        'file': (json.dumps(valid_geojson), 'field.geojson')
    }

    response = client.post('/api/register-field', data=data, content_type='multipart/form-data')
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data['status'] == 'VALIDATED'
    assert json_data['field_name'] == 'Test_Field_01'
    assert json_data['spatial_integrity_verified'] is True


def test_register_field_self_intersection(client):
    invalid_geojson = {
        "features": [
            {
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-86.0, 35.0],
                            [-86.1, 35.1],
                            [-86.0, 35.1],
                            [-86.1, 35.0],
                            [-86.0, 35.0]
                        ]
                    ]
                }
            }
        ]
    }

    data = {
        'fieldName': 'Invalid_Field',
        'soilType': 'Crider Silt Loam',
        'file': (json.dumps(invalid_geojson), 'invalid.geojson')
    }

    response = client.post('/api/register-field', data=data, content_type='multipart/form-data')
    json_data = response.get_json()

    assert response.status_code == 422
    assert "Spatial Validation Failure" in json_data['error']


def test_register_field_missing_file(client):
    data = {
        'fieldName': 'No_File_Field',
        'soilType': 'Other'
    }

    response = client.post('/api/register-field', data=data, content_type='multipart/form-data')
    json_data = response.get_json()

    assert response.status_code == 400
    assert json_data['error'] == "No file uploaded."
