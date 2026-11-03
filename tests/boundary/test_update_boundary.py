import os
import allure
import pytest
from config import settings
from services.crop_service import CropService
from utils.data_loader import load_json
from utils.assertions import assert_status, response_json
from utils.allure_helpers import attach_response

@allure.epic("Krishivaas API Automation")
@allure.feature("Crop Management")
@allure.story("Update Crop")
@allure.title("Update existing crop allocation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_update_crop(api_client):
    crop_allocation_id = settings.env_id("EXISTING_CROP_ALLOCATION_ID")
    farm_id = settings.env_id("EXISTING_CROP_FARM_ID") or settings.env_id("EXISTING_FARM_ID")
    farmer_id = settings.env_id("EXISTING_CROP_FARMER_ID") or settings.env_id("EXISTING_FARMER_ID")
    if not crop_allocation_id or not farm_id or not farmer_id:
        pytest.skip("Set EXISTING_CROP_ALLOCATION_ID, EXISTING_FARM_ID and EXISTING_FARMER_ID.")
    with allure.step("Prepare Update Crop data"):
        fields = load_json("crop_data.json")["update"].copy()
        fields.update({"fmr_id": farmer_id, "flu_id": farm_id,
                       "token": os.getenv("API_TOKEN", "")})
    with allure.step(f"Update crop allocation {crop_allocation_id}"):
        response = CropService(api_client).update_crop(crop_allocation_id, fields)
        attach_response(response, "Update Crop response")
    with allure.step("Validate response"):
        assert_status(response)
        print("Update crop response:", response_json(response))
