
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
@allure.story("Update Farm")
@allure.title("Verify Update Farm API updates an existing farm")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_update_farm(api_client):

    with allure.step("1. Load Update Farm test data"):

        farm_id = settings.env_id("EXISTING_FARM_ID")
        farmer_id = settings.env_id("EXISTING_FARMER_ID")

        if not farm_id or not farmer_id:
            pytest.skip(
                "Set EXISTING_FARM_ID and EXISTING_FARMER_ID in .env."
            )

        fields = load_json("farm_data.json")["update"].copy()

        mobile_number = os.getenv("TEST_MOBILE_NUMBER", "").strip()
        mapindia_token = os.getenv("MAPINDIA_TOKEN", "").strip()

        if not mobile_number:
            pytest.fail("TEST_MOBILE_NUMBER is missing from .env")

        if not mapindia_token:
            pytest.fail("MAPINDIA_TOKEN is missing from .env")

        fields.update({
            "contact_number": mobile_number,
            "mapIndia_token": mapindia_token,
            "contact_person_id": str(farmer_id),
        })

        expected = {
            "success": True,
        }

        allure.dynamic.parameter("Farm ID", str(farm_id))
        allure.dynamic.parameter("Farmer ID", str(farmer_id))
        allure.dynamic.parameter("Farm Name", fields.get("farm_name", ""))

        logger.info("Update Farm test data loaded.")

    with allure.step("2. Send Update Farm API request"):

        response = FarmService(api_client).update_farm(
            fields=fields,
            farmer_id=farmer_id,
            farm_id=farm_id,
        )

        attach_api_details(
            response=response,
            operation="Update Farm",
            request_body=fields,
            identifiers={
                "Farm ID": farm_id,
                "Farmer ID": farmer_id,
                "Farm Name": fields.get("farm_name"),
            },
            expected_response=expected,
        )

    with allure.step("3. Validate HTTP response status"):

        assert_status(response)

    with allure.step("4. Compare actual and expected response"):

        body = response_json(response)

        print("Update Farm response:", body)

        assert isinstance(body, dict), (
            f"Expected a JSON object response. Actual: {body}"
        )

        assert_response_matches(body, expected)

        logger.info("Update Farm API response validated successfully.")
