
import os
import logging
import allure
import pytest

from config import settings
from services.farm_service import FarmService
from utils.data_loader import load_json
from utils.assertions import (
    assert_status,
    response_json,
    assert_response_matches,
)
from utils.allure_helpers import attach_api_details

logger = logging.getLogger(__name__)


@allure.epic("Krishivaas API Automation")
@allure.feature("Farm Management")
@allure.story("Add Farm")
@allure.title("Verify Add Farm API creates a farm")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_add_farm(api_client):

    with allure.step("1. Load Add Farm test data"):

        farmer_id = settings.env_id("EXISTING_FARMER_ID")

        if not farmer_id:
            pytest.skip("Set EXISTING_FARMER_ID in .env or run Add Farmer first.")

        fields = load_json("farm_data.json")["add"].copy()

        mobile_number = os.getenv("TEST_MOBILE_NUMBER", "").strip()
        mapindia_token = os.getenv("MAPINDIA_TOKEN", "").strip()

        if not mobile_number:
            pytest.fail("TEST_MOBILE_NUMBER is missing from .env")

        if not mapindia_token:
            pytest.fail("MAPINDIA_TOKEN is missing from .env")

        fields.update({
            "contact_person_id": str(farmer_id),
            "contact_number": mobile_number,
            "mapIndia_token": mapindia_token,
        })

        expected = {
            "success": True,
        }

        allure.dynamic.parameter("Farmer ID", str(farmer_id))
        allure.dynamic.parameter("Farm Name", fields.get("farm_name", ""))
        allure.dynamic.parameter("Contact Number", mobile_number)

        logger.info("Add Farm test data loaded.")

    with allure.step("2. Send Add Farm API request"):

        response = FarmService(api_client).add_farm(fields)

        attach_api_details(
            response=response,
            operation="Add Farm",
            request_body=fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm Name": fields.get("farm_name"),
                "Contact Number": mobile_number,
            },
            expected_response=expected,
        )

    with allure.step("3. Validate HTTP response status"):

        assert_status(response)

    with allure.step("4. Compare actual and expected response"):

        body = response_json(response)

        print("Add Farm response:", body)

        assert isinstance(body, dict), (
            f"Expected a JSON object response. Actual: {body}"
        )

        assert_response_matches(body, expected)

        logger.info("Add Farm API response validated successfully.")
