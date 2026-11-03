import json
import logging
import os

import allure
import pytest

from services.farmer_service import FarmerService
from services.farm_service import FarmService
from services.crop_service import CropService
from services.boundary_service import BoundaryService
from utils.data_loader import load_json
from utils.assertions import assert_status, response_json, assert_response_matches

logger = logging.getLogger(__name__)

SENSITIVE_KEY_PARTS = (
    "token", "authorization", "password", "secret", "api_key", "apikey", "cookie"
)


def mask_sensitive_data(value):
    """Mask credentials recursively before displaying or attaching API data."""
    if isinstance(value, dict):
        return {
            key: (
                "***MASKED***"
                if any(part in str(key).lower() for part in SENSITIVE_KEY_PARTS)
                else mask_sensitive_data(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [mask_sensitive_data(item) for item in value]
    return value


def attach_workflow_api_details(
    response, operation, request_body=None, identifiers=None, expected_response=None
):
    """Attach useful API details to Allure without exposing credentials."""
    try:
        actual_response = response.json()
    except (ValueError, AttributeError):
        actual_response = getattr(response, "text", "Response body unavailable")

    details = {
        "operation": operation,
        "http_status_code": getattr(response, "status_code", None),
        "identifiers": identifiers or {},
        "request_body": mask_sensitive_data(request_body or {}),
        "expected_response": mask_sensitive_data(expected_response or {}),
        "actual_response": mask_sensitive_data(actual_response),
    }
    allure.attach(
        json.dumps(details, indent=4, ensure_ascii=False, default=str),
        name=f"{operation} - API Details",
        attachment_type=allure.attachment_type.JSON,
    )


def extract_id(data, *keys):
    """Find a generated ID in a nested API response."""
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if value not in (None, ""):
                return value
        for value in data.values():
            found = extract_id(value, *keys)
            if found not in (None, ""):
                return found
    elif isinstance(data, list):
        for item in data:
            found = extract_id(item, *keys)
            if found not in (None, ""):
                return found
    return None


def validate_api_response(response, operation, expected):
    """Validate HTTP status and API business response."""
    assert_status(response)
    body = response_json(response)
    print(f"\n{operation} response:", mask_sensitive_data(body))
    assert isinstance(body, dict), (
        f"{operation}: Expected JSON object. Actual: {mask_sensitive_data(body)}"
    )
    assert_response_matches(body, expected)
    return body


def attach_created_id(name, value):
    allure.dynamic.parameter(name, str(value))
    allure.attach(
        str(value),
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


def require_env(name):
    value = os.getenv(name, "").strip()
    if not value:
        pytest.fail(f"{name} is missing from .env")
    return value


@allure.epic("Krishivaas API Automation")
@allure.feature("End-to-End API Testing")
@allure.story("Farmer → Farm → Crop → Boundary")
@allure.title(
    "Complete E2E workflow: Add and Update Farmer, Farm, Crop and Boundary"
)
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.integration
def test_farmer_farm_crop_boundary(api_client):
    farmer_service = FarmerService(api_client)
    farm_service = FarmService(api_client)
    crop_service = CropService(api_client)
    boundary_service = BoundaryService(api_client)

    mapindia_token = require_env("MAPINDIA_TOKEN")
    api_token = require_env("API_TOKEN")
    farm_contact_number = require_env("TEST_MOBILE_NUMBER")

    # STEP 1: ADD FARMER
    with allure.step("1. Add Farmer"):
        farmer_fields = load_json("farmer_data.json")["add"].copy()

        if farmer_fields.get("mapIndia_token") in (None, "", "${MAPINDIA_TOKEN}"):
            farmer_fields["mapIndia_token"] = mapindia_token

        farmer_mobile_number = farmer_fields.get("mobile_number")
        assert farmer_mobile_number, (
            "farmer_data.json -> add.mobile_number is required"
        )

        farmer_expected = {
            "success": True,
            "message": "Farmer added successfully.!",
        }

        allure.dynamic.parameter("Farmer Name", farmer_fields.get("first_name", ""))
        allure.dynamic.parameter("Farmer Mobile", str(farmer_mobile_number))

        response = farmer_service.add_farmer(farmer_fields)
        attach_workflow_api_details(
            response=response,
            operation="E2E - Add Farmer",
            request_body=farmer_fields,
            identifiers={
                "Farmer Name": farmer_fields.get("first_name"),
                "Farmer Mobile": farmer_mobile_number,
            },
            expected_response=farmer_expected,
        )
        farmer_body = validate_api_response(
            response, "Add Farmer", farmer_expected
        )
        farmer_id = extract_id(farmer_body, "fmr_id")
        assert farmer_id is not None, (
            "Farmer ID (fmr_id) not found in Add Farmer response."
        )
        attach_created_id("Created Farmer ID", farmer_id)

    # STEP 2: UPDATE FARMER
    with allure.step("2. Update Farmer"):
        farmer_update_fields = load_json("farmer_data.json")["update"].copy()

        # The backend rejected the previous request because mobile_number
        # was missing. Reuse the number used to create this farmer.
        farmer_update_fields["mobile_number"] = str(farmer_mobile_number)
        farmer_update_fields["fmr_id"] = str(farmer_id)

        farmer_update_expected = {
            "success": True,
            "message": "Farmer data updated successfully.!",
        }
        allure.dynamic.parameter("Updating Farmer ID", str(farmer_id))

        response = farmer_service.update_farmer(
            farmer_update_fields, farmer_id
        )
        attach_workflow_api_details(
            response=response,
            operation="E2E - Update Farmer",
            request_body=farmer_update_fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farmer Mobile": farmer_mobile_number,
            },
            expected_response=farmer_update_expected,
        )
        validate_api_response(
            response, "Update Farmer", farmer_update_expected
        )

    # STEP 3: ADD FARM
    with allure.step("3. Add Farm"):
        farm_fields = load_json("farm_data.json")["add"].copy()
        farm_fields.update({
            "contact_person_id": str(farmer_id),
            "contact_number": farm_contact_number,
            "mapIndia_token": mapindia_token,
        })
        farm_expected = {"success": True}

        allure.dynamic.parameter("Farm Contact Farmer ID", str(farmer_id))
        allure.dynamic.parameter("Farm Name", farm_fields.get("farm_name", ""))

        response = farm_service.add_farm(farm_fields)
        attach_workflow_api_details(
            response=response,
            operation="E2E - Add Farm",
            request_body=farm_fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm Name": farm_fields.get("farm_name"),
            },
            expected_response=farm_expected,
        )
        farm_body = validate_api_response(response, "Add Farm", farm_expected)
        farm_id = extract_id(
            farm_body,
            "id",
            "flu_id",
            "farm_id"
        )

        assert farm_id is not None, (
            f"Farm ID not found in Add Farm response: {farm_body}"
        )

        attach_created_id("Created Farm ID", farm_id)
        assert farm_id is not None, (
            "Farm ID (flu_id/farm_id) not found in Add Farm response."
        )
        attach_created_id("Created Farm ID", farm_id)

    # STEP 4: UPDATE FARM
    with allure.step("4. Update Farm"):
        farm_update_fields = load_json("farm_data.json")["update"].copy()
        farm_update_fields.update({
            "contact_number": farm_contact_number,
            "mapIndia_token": mapindia_token,
            "contact_person_id": str(farmer_id),
        })
        farm_expected = {"success": True}

        response = farm_service.update_farm(
            fields=farm_update_fields,
            farmer_id=farmer_id,
            farm_id=farm_id,
        )
        attach_workflow_api_details(
            response=response,
            operation="E2E - Update Farm",
            request_body=farm_update_fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm ID": farm_id,
                "Farm Name": farm_update_fields.get("farm_name"),
            },
            expected_response=farm_expected,
        )
        validate_api_response(response, "Update Farm", farm_expected)

    # STEP 5: ADD CROP
    with allure.step("5. Add Crop"):
        crop_fields = load_json("crop_data.json")["add"].copy()
        crop_fields.update({
            "fmr_id": str(farmer_id),
            "flu_id": str(farm_id),
            "token": api_token,
        })
        crop_expected = {"success": True}

        allure.dynamic.parameter("Crop Name", crop_fields.get("crop_name", ""))
        allure.dynamic.parameter("Crop Catalogue ID", crop_fields.get("ccn_id", ""))

        response = crop_service.add_crop(crop_fields)
        attach_workflow_api_details(
            response=response,
            operation="E2E - Add Crop",
            request_body=crop_fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm ID": farm_id,
                "Crop Name": crop_fields.get("crop_name"),
                "Crop Catalogue ID": crop_fields.get("ccn_id"),
            },
            expected_response=crop_expected,
        )
        crop_body = validate_api_response(response, "Add Crop", crop_expected)
        crop_allocation_id = extract_id(
            crop_body, "cfa_id", "allocation_id", "crop_allocation_id"
        )
        assert crop_allocation_id is not None, (
            "Crop allocation ID not found in Add Crop response. "
            "Check the actual response field name."
        )
        attach_created_id("Created Crop Allocation ID", crop_allocation_id)

    # STEP 6: UPDATE CROP
    with allure.step("6. Update Crop"):
        crop_update_fields = load_json("crop_data.json")["update"].copy()
        crop_expected = {"success": True}

        response = crop_service.update_crop(
            fields=crop_update_fields,
            farmer_id=farmer_id,
            farm_id=farm_id,
            crop_allocation_id=crop_allocation_id,
        )
        attach_workflow_api_details(
            response=response,
            operation="E2E - Update Crop",
            request_body=crop_update_fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm ID": farm_id,
                "Crop Allocation ID": crop_allocation_id,
                "Crop Name": crop_update_fields.get("crop_name"),
            },
            expected_response=crop_expected,
        )
        validate_api_response(response, "Update Crop", crop_expected)

    # STEP 7: ADD BOUNDARY
    with allure.step("7. Add Boundary"):
        boundary_fields = load_json("boundary_data.json")["add"].copy()
        boundary_fields["farm_id"] = str(farm_id)
        boundary_expected = {"success": True}

        allure.dynamic.parameter("Boundary Farm ID", str(farm_id))

        response = boundary_service.add_boundary(boundary_fields)
        attach_workflow_api_details(
            response=response,
            operation="E2E - Add Boundary",
            request_body=boundary_fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm ID": farm_id,
                "Crop Allocation ID": crop_allocation_id,
                "Boundary Area": boundary_fields.get("farm_calculated_area"),
                "Boundary Area Unit": boundary_fields.get(
                    "farm_calculated_area_unit"
                ),
            },
            expected_response=boundary_expected,
        )
        validate_api_response(response, "Add Boundary", boundary_expected)

    # STEP 8: FINAL E2E SUMMARY
    with allure.step("8. E2E Workflow Summary"):
        summary = {
            "workflow": "Farmer → Farm → Crop → Boundary",
            "farmer_id": str(farmer_id),
            "farmer_mobile_number": str(farmer_mobile_number),
            "farm_id": str(farm_id),
            "crop_allocation_id": str(crop_allocation_id),
            "farmer_status": "Success",
            "farm_status": "Success",
            "crop_status": "Success",
            "boundary_status": "Success",
            "overall_status": "Success",
        }
        allure.attach(
            json.dumps(summary, indent=4, ensure_ascii=False),
            name="Complete E2E Workflow Summary",
            attachment_type=allure.attachment_type.JSON,
        )
        for key, value in summary.items():
            allure.dynamic.parameter(key, str(value))

        logger.info("Complete Farmer-Farm-Crop-Boundary workflow passed.")
        print("\n========== E2E WORKFLOW SUCCESS ==========")
        print(json.dumps(summary, indent=4, ensure_ascii=False))
        print("==========================================\n")
