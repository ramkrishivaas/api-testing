
import logging
import allure
import pytest

from config import settings
from services.boundary_service import BoundaryService
from utils.data_loader import load_json
from utils.assertions import (
    assert_status,
    response_json,
    assert_response_matches,
)
from utils.allure_helpers import attach_api_details

logger = logging.getLogger(__name__)


@allure.epic("Krishivaas API Automation")
@allure.feature("Farm Boundary Management")
@allure.story("Add Boundary")
@allure.title("Verify Add Boundary API adds boundary to an existing farm")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.integration
def test_add_boundary(api_client):

    with allure.step("1. Load Add Boundary test data"):

        farm_id = (
            settings.env_id("EXISTING_BOUNDARY_FARM_ID")
            or settings.env_id("EXISTING_FARM_ID")
        )

        if not farm_id:
            pytest.skip("Set EXISTING_FARM_ID in .env.")

        fields = load_json("boundary_data.json")["add"].copy()
        fields["farm_id"] = str(farm_id)

        expected = {
            "success": True,
        }

        allure.dynamic.parameter("Farm ID", str(farm_id))
        allure.dynamic.parameter(
            "Boundary Area",
            fields.get("farm_calculated_area", "")
        )
        allure.dynamic.parameter(
            "Boundary Area Unit",
            fields.get("farm_calculated_area_unit", "")
        )
        allure.dynamic.parameter(
            "Boundary Method",
            fields.get("boundary_method_type", "")
        )

        logger.info("Add Boundary test data loaded.")

    with allure.step("2. Send Add Boundary API request"):

        response = BoundaryService(api_client).add_boundary(fields)

        attach_api_details(
            response=response,
            operation="Add Boundary",
            request_body=fields,
            identifiers={
                "Farm ID": farm_id,
                "Boundary Area": fields.get("farm_calculated_area"),
                "Boundary Area Unit": fields.get(
                    "farm_calculated_area_unit"
                ),
                "Boundary Method": fields.get("boundary_method_type"),
            },
            expected_response=expected,
        )

    with allure.step("3. Validate HTTP response status"):

        assert_status(response)

    with allure.step("4. Compare actual and expected response"):

        body = response_json(response)

        print("Add Boundary response:", body)

        assert isinstance(body, dict), (
            f"Expected a JSON object response. Actual: {body}"
        )

        assert_response_matches(body, expected)

        logger.info("Add Boundary API response validated successfully.")
