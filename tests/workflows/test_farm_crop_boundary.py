"""Uses existing farmer/farm IDs, adds crop, then submits boundary for that farm."""
import os
import pytest
from config import settings
from services.farm_service import FarmService
from services.crop_service import CropService
from services.boundary_service import BoundaryService
from utils.data_loader import load_json
from utils.assertions import assert_status, response_json

@pytest.mark.integration
def test_farm_crop_boundary(api_client):
    farm_id = settings.env_id("EXISTING_FARM_ID")
    farmer_id = settings.env_id("EXISTING_FARMER_ID")
    if not farm_id or not farmer_id:
        pytest.skip("Set EXISTING_FARM_ID and EXISTING_FARMER_ID in .env.")
    crop_fields = load_json("crop_data.json")["add"]
    crop_fields.update({"flu_id": farm_id, "fmr_id": farmer_id, "token": os.getenv("API_TOKEN", "")})
    crop_response = CropService(api_client).add_crop(crop_fields)
    assert_status(crop_response)

    boundary_fields = load_json("boundary_data.json")["add"]
    boundary_fields["farm_id"] = farm_id
    cfa_id = settings.env_id("EXISTING_BOUNDARY_CFA_ID")
    if cfa_id:
        boundary_fields["cfa_id"] = cfa_id
    boundary_response = BoundaryService(api_client).add_boundary(boundary_fields)
    assert_status(boundary_response)
    print("Farm/crop/boundary responses:",
          {"crop": response_json(crop_response), "boundary": response_json(boundary_response)})
