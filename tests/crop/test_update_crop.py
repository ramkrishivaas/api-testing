
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
@allure.story("Update Crop")
@allure.title("Verify Update Crop API updates an existing crop allocation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_update_crop(api_client):

    with allure.step("1. Load Update Crop test data"):

        farmer_id = settings.env_id("EXISTING_FARMER_ID")
        farm_id = settings.env_id("EXISTING_FARM_ID")
        crop_allocation_id = settings.env_id("EXISTING_CROP_ID")

        if not farmer_id or not farm_id or not crop_allocation_id:
            pytest.skip(
                "Set EXISTING_FARMER_ID, EXISTING_FARM_ID "
                "and EXISTING_CROP_ID in .env."
            )

        fields = load_json("crop_data.json")["update"].copy()

        expected = {
            "success": True,
        }

        allure.dynamic.parameter("Farmer ID", str(farmer_id))
        allure.dynamic.parameter("Farm ID", str(farm_id))
        allure.dynamic.parameter(
            "Crop Allocation ID", str(crop_allocation_id)
        )
        allure.dynamic.parameter("Crop Name", fields.get("crop_name", ""))

        logger.info("Update Crop test data loaded.")

    with allure.step("2. Send Update Crop API request"):

        response = CropService(api_client).update_crop(
            fields=fields,
            farmer_id=farmer_id,
            farm_id=farm_id,
            crop_allocation_id=crop_allocation_id,
        )

        attach_api_details(
            response=response,
            operation="Update Crop",
            request_body=fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farm ID": farm_id,
                "Crop Allocation ID": crop_allocation_id,
                "Crop Name": fields.get("crop_name"),
            },
            expected_response=expected,
        )

    with allure.step("3. Validate HTTP response status"):

        assert_status(response)

    with allure.step("4. Compare actual and expected response"):

        body = response_json(response)

        print("Update Crop response:", body)

        assert isinstance(body, dict), (
            f"Expected a JSON object response. Actual: {body}"
        )

        assert_response_matches(body, expected)

        logger.info("Update Crop API response validated successfully.")
