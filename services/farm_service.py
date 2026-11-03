from utils.multipart import multipart_fields


class FarmService:
    def __init__(self, api_client):
        self.client = api_client

    def add_farm(self, fields):
        return self.client.post(
            "/api/v1/add-farm-post-mobile",
            files=multipart_fields(fields),
        )

    def update_farm(self, fields, farmer_id, farm_id):
        payload = fields.copy()
        payload["fmr_id"] = str(farmer_id)
        payload["flu_id"] = str(farm_id)
    
        return self.client.post(
            "/api/v1/update-farm",
            files=multipart_fields(payload),
        )