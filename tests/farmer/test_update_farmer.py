import os
import allure
import pytest
from config import settings
from services.farmer_service import FarmerService
from utils.data_loader import load_json
from utils.assertions import assert_status, response_json
from utils.allure_helpers import attach_response, attach_api_details

@allure.epic("Krishivaas API Automation")
@allure.feature("Farmer Management")
@allure.story("Update Farmer")
@allure.title("Update existing farmer")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_update_farmer(api_client):
    farmer_id = settings.env_id("EXISTING_FARMER_ID")
    if not farmer_id:
        pytest.skip("Set EXISTING_FARMER_ID in .env.")
    with allure.step("Prepare Update Farmer data"):
        fields = load_json("farmer_data.json")["update"].copy()
        fields.update({
            "chk_dummy_contact": "N",
            "mobile_number": os.getenv("TEST_MOBILE_NUMBER", ""),
            "email": "",
            "business_unit": os.getenv("BUSINESS_UNIT", "devqa(All)"),
            "businessunit_hiddenfield": os.getenv("BUSINESS_UNIT_ID", "333"),
            "agent": os.getenv("AGENT_NAME", "Aryan New FA1"),
            "agent_id": os.getenv("AGENT_ID", "3411"),
            "preferred_language": "English",
            "country": "India",
            "countryCode": " +91",
            "crop_details": "[]",
        })
    with allure.step(f"Update farmer fmr_id={farmer_id}"):

        response = FarmerService(api_client).update_farmer(
            fields, farmer_id
        )
    
        attach_api_details(
            response=response,
            operation="Update Farmer",
            request_body=fields,
            identifiers={
                "Farmer ID": farmer_id,
                "Farmer Name": fields.get("first_name"),
                "Farmer Mobile": fields.get("mobile_number"),
            },
        )

    with allure.step("Validate Update Farmer response"):
    
        assert_status(response)
    
        body = response_json(response)
    
        assert isinstance(body, dict), (
            "Expected a JSON object response."
        )
    with allure.step("Validate response"):
        assert_status(response)
        print("Update farmer response:", response_json(response))
