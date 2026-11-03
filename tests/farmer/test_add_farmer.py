
import os
import logging
import allure
import pytest

from services.farmer_service import FarmerService
from utils.data_loader import load_json
from utils.assertions import assert_status, response_json, assert_response_matches
from utils.allure_helpers import attach_api_details

logger = logging.getLogger(__name__)


@allure.epic("Krishivaas API Automation")
@allure.feature("Farmer Management")
@allure.story("Add Farmer")
@allure.title("Verify Add Farmer API creates a farmer")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_add_farmer(api_client):

    with allure.step("1. Load Add Farmer test data"):

        fields = load_json("farmer_data.json")["add"].copy()

        mapindia_token = os.getenv("MAPINDIA_TOKEN", "").strip()

        if fields.get("mapIndia_token") == "${MAPINDIA_TOKEN}":
            fields["mapIndia_token"] = mapindia_token

        if not fields.get("mapIndia_token"):
            pytest.fail("MAPINDIA_TOKEN is missing from .env")

        # Expected successful creation response.
        expected = {
            "success": True,
            "message": "Farmer added successfully.!",
        }

        logger.info("Add Farmer test data loaded.")

        # Display test inputs in Allure before sending request.
        allure.dynamic.parameter("Farmer Name", fields.get("first_name", ""))
        allure.dynamic.parameter("Farmer Mobile", fields.get("mobile_number", ""))

    with allure.step("2. Send Add Farmer API request"):

        response = FarmerService(api_client).add_farmer(fields)

        # Attach request, response and test details before assertions.
        attach_api_details(
            response=response,
            operation="Add Farmer",
            request_body=fields,
            identifiers={
                "Farmer Name": fields.get("first_name"),
                "Farmer Mobile": fields.get("mobile_number"),
            },
            expected_response=expected,
        )

    with allure.step("3. Validate HTTP response status"):

        assert_status(response)

    with allure.step("4. Compare actual and expected response"):

        body = response_json(response)

        assert isinstance(body, dict), (
            "Expected a JSON object response."
        )

        assert_response_matches(body, expected)

    with allure.step("5. Validate created farmer ID"):

        farmer_data = body.get("data")

        assert isinstance(farmer_data, dict), (
            "Expected a data object in the response."
        )

        fmr_id = farmer_data.get("fmr_id")

        assert str(fmr_id).isdigit() and int(fmr_id) > 0, (
            f"Expected a positive numeric farmer ID; got {fmr_id!r}"
        )

        # Add the dynamically generated ID to Allure.
        allure.dynamic.parameter("Created Farmer ID", str(fmr_id))

        logger.info("Add Farmer API returned a valid farmer ID.")
