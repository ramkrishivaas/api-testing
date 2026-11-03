
from utils.multipart import multipart_fields


class CropService:
    """Service methods for crop allocation operations."""

    ADD_CROP_ENDPOINT = "/api/v1/customer/add-crop-allocation"
    UPDATE_CROP_ENDPOINT = "/api/v1/customer/farmer-allocation/{}/update"

    def __init__(self, api_client):
        self.client = api_client

    def add_crop(self, fields):
        if not isinstance(fields, dict):
            raise TypeError("fields must be a dictionary")

        payload = fields.copy()

        return self.client.post(
            self.ADD_CROP_ENDPOINT,
            files=multipart_fields(payload),
        )

    def update_crop(self, fields, farmer_id, farm_id, crop_allocation_id):
        if not isinstance(fields, dict):
            raise TypeError("fields must be a dictionary")

        if not farmer_id or not farm_id or not crop_allocation_id:
            raise ValueError(
                "farmer_id, farm_id and crop_allocation_id are required"
            )

        payload = fields.copy()
        payload["fmr_id"] = str(farmer_id)
        payload["flu_id"] = str(farm_id)

        endpoint = self.UPDATE_CROP_ENDPOINT.format(crop_allocation_id)

        return self.client.post(
            endpoint,
            files=multipart_fields(payload),
        )
