
import json
import allure


SENSITIVE_KEYS = {
    "token",
    "mapindia_token",
    "authorization",
    "password",
    "access_token",
    "refresh_token",
    "api_key",
}


def sanitize_data(data):
    """Remove secrets before attaching data to Allure."""

    if isinstance(data, dict):
        sanitized = {}

        for key, value in data.items():
            if any(secret in key.lower() for secret in SENSITIVE_KEYS):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = sanitize_data(value)

        return sanitized

    if isinstance(data, list):
        return [sanitize_data(item) for item in data]

    return data


def attach_json(name, data):
    """Attach structured JSON data to Allure."""

    safe_data = sanitize_data(data)

    allure.attach(
        json.dumps(
            safe_data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def add_test_parameters(parameters):
    """Display important test input values in Allure."""

    for name, value in parameters.items():
        if value is not None and value != "":
            allure.dynamic.parameter(str(name), str(value))


def attach_response(response, name="API Response"):
    """Attach actual API response without request headers."""

    try:
        body = response.json()
    except (ValueError, AttributeError):
        body = getattr(response, "text", "<No response body>")

    attach_json(name, body)


def attach_api_details(
    response,
    operation,
    request_body=None,
    identifiers=None,
    expected_response=None,
):
    """
    Common Allure reporting for API requests.

    Call immediately after receiving the API response,
    before assertions.
    """

    identifiers = identifiers or {}

    # Display test inputs in Allure.
    parameters = {
        "API Operation": operation,
        **identifiers,
    }

    add_test_parameters(parameters)

    # Attach request body.
    if request_body is not None:
        attach_json("Request Body", request_body)

    # Attach expected response when provided.
    if expected_response is not None:
        attach_json("Expected Response", expected_response)

    # Attach actual response.
    attach_response(response, "Actual Response")

    # Attach useful API execution details.
    details = {
        "operation": operation,
        "http_status": getattr(response, "status_code", None),
        "response_time_ms": round(
            response.elapsed.total_seconds() * 1000, 2
        ) if getattr(response, "elapsed", None) else None,
        "request_method": getattr(response.request, "method", None),
        "request_url": getattr(response.request, "url", None),
    }

    allure.attach(
        json.dumps(details, indent=2, default=str),
        name="API Execution Details",
        attachment_type=allure.attachment_type.JSON,
    )
