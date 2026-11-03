
from utils.multipart import multipart_fields


class FarmerService:

    def __init__(self, api_client):
        self.client = api_client

    def add_farmer(self, fields):
        """Create a farmer using the Add Farmer API."""

        payload = fields.copy()
        payload["fmr_id"] = ""
        payload["access_type"] = "add_access"

        return self.client.post(
            "/api/v1/save-farmer-detail",
            files=multipart_fields(payload),
        )

    def update_farmer(self, fields, farmer_id):
        """Update an existing farmer."""

        if farmer_id is None or not str(farmer_id).strip():
            raise ValueError(
                "farmer_id is required to update a farmer."
            )

        payload = fields.copy()
        payload["fmr_id"] = str(farmer_id)
        payload["access_type"] = "edit_access"

        return self.client.post(
            "/api/v1/save-farmer-detail",
            files=multipart_fields(payload),
        )
