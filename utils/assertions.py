import json
import allure
from jsonschema import validate as jsonschema_validate

def response_text(response):
    try:
        return json.dumps(response.json(), ensure_ascii=False, indent=2)
    except ValueError:
        return response.text

def assert_status(response, expected=(200, 201)):
    assert response.status_code in expected, (
        f"Expected status in {expected}; got {response.status_code}.\n"
        f"Response: {response_text(response)}"
    )

def assert_json_fields(actual, expected):
    """Compare the expected fields with the actual API response."""

    for key, expected_value in expected.items():
        assert key in actual, (
            f"Missing field: {key}. Actual response: {actual}"
        )

        assert actual[key] == expected_value, (
            f"Mismatch for '{key}'. "
            f"Expected: {expected_value!r}; "
            f"Actual: {actual[key]!r}"
        )


def attach_json(name, data):
    """Attach JSON data to Allure for debugging."""

    allure.attach(
        json.dumps(data, indent=2, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def assert_response_matches(actual, expected):
    """Attach and compare expected versus actual JSON fields."""

    attach_json("Expected API Response", expected)
    attach_json("Actual API Response", actual)

    assert_json_fields(actual, expected)

def assert_json_schema(response, schema):
    try:
        body = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"Expected JSON response, got Content-Type={response.headers.get('Content-Type')!r}; "
            f"body={response.text[:1000]!r}"
        ) from exc
    jsonschema_validate(instance=body, schema=schema)

def extract_id(payload, candidate_keys):
    """Search nested response JSON for the first non-empty ID in candidate_keys."""
    if isinstance(payload, dict):
        for key in candidate_keys:
            value = payload.get(key)
            if value not in (None, ""):
                return value
        for value in payload.values():
            found = extract_id(value, candidate_keys)
            if found not in (None, ""):
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = extract_id(value, candidate_keys)
            if found not in (None, ""):
                return found
    return None

def response_json(response):
    try:
        return response.json()
    except ValueError:
        return {"raw_text": response.text}


def validate_payload_fields(payload, required_fields):
    """Check required fields and identify empty values."""

    missing = [
        field for field in required_fields
        if field not in payload
    ]

    empty = [
        field for field in required_fields
        if field in payload and payload[field] in (None, "")
    ]

    if missing or empty:
        raise AssertionError(
            f"Missing fields: {missing}; Empty fields: {empty}"
        )

    return True
