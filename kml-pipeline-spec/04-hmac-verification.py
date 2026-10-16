"""
IoT scale-house payload verification.
Verifies cryptographic integrity and field association of incoming
weight payloads before smart contract execution.
PROPOSED ARCHITECTURE — not deployed.
"""
import hmac
import hashlib
import json


def verify_scale_house_payload(payload: dict, expected_field_hash: str, shared_secret: str) -> bool:
    """
    Verifies the cryptographic integrity and field association of an incoming
    IoT scale house weight payload before smart contract execution.
    """
    # 1. Verify that the payload references the correct registered field hash
    if payload.get("field_polygon_hash") != expected_field_hash:
        return False

    # 2. Extract and remove signature for verification
    received_signature = payload.pop("hmac_signature", None)
    if not received_signature:
        return False

    # 3. Recalculate HMAC using the shared secret and canonical payload string
    canonical_payload = json.dumps(payload, sort_keys=True)
    calculated_signature = hmac.new(
        shared_secret.encode('utf-8'),
        canonical_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 4. Secure constant-time comparison
    return hmac.compare_digest(received_signature, calculated_signature)
