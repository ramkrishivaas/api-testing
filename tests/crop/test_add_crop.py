
import os
import logging
import allure
import pytest

from config import settings
from services.crop_service import CropService
from utils.data_loader import load_json
from utils.assertions import (
    assert_status,
    response_json,
    assert_response_matches,
)
from utils.allure_helpers import attach_api_details

logger = logging.getLogger(__name__)


@allure.epic("Krishivaas API Automation")
@allure.feature("Crop Management")
@allure.story("Add Crop")
@allure.title("Verify Add Crop API creates a crop allocation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_add_crop(api_client):

    with allure.step("1. Load Add Crop test data"):

        farmer_id = settings.env_id("EXISTING_FARMER_ID")
        farm_id = settings.env_id("EXISTING_FARM_ID")

        if not farmer_id or not farm_id:
            pytest.skip(
                "Set EXISTING_FARMER_ID and EXISTING_FARM_ID in .env."
            )

        fields = load_json("crop_data.json")["add"].copy()

        api_token = os.getenv("API_TOKEN", "").strip()

        if not api_token:
            pytest.fail("API_TOKEN is missing from .env")

        fields.update({
            "flu_id": str(farm_id),
            "fmr_id": str(farmer_id),
            "token": api_token,
        })

        expected = {
            "success": True,
        }

        allure.dynamic.parameter("Farmer ID", str(farmer_id))
        allure.dynamic.parameter("Farm ID", str(farm_id))
        allure.dynamic.parameter("Crop Name", fields.get("crop_name", ""))
        allure.dynamic.parameter("Crop Catalogue ID", fields.get("ccn_id", ""))

        logger.info("Add Crop test data loaded.")

    with allure.step("2. Send Add Crop API request"):

        response = CropService(api_client).add_crop(fields)

        attach_api_details(
            response=response,
            operation="Add Crop",
            request_body=fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm ID": farm_id,
                "Crop Name": fields.get("crop_name"),
                "Crop Catalogue ID": fields.get("ccn_id"),
            },
            expected_response=expected,
        )

    with allure.step("3. Validate HTTP response status"):

        assert_status(response)

    with allure.step("4. Compare actual and expected response"):

        body = response_json(response)

        print("Add Crop response:", body)

        assert isinstance(body, dict), (
            f"Expected a JSON object response. Actual: {body}"
        )

        assert_response_matches(body, expected)

        logger.info("Add Crop API response validated successfully.")
