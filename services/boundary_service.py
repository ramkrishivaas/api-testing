
class BoundaryService:
    """Service methods for farm boundary operations."""

    ENDPOINT = "/api/v1/update-farm-boundry-for-mobile"

    def __init__(self, client):
        self.client = client

    def add_boundary(self, fields):
        payload = self._validate(fields)

        return self.client.post(
            self.ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            },
        )

    def update_boundary(self, fields):
        payload = self._validate(fields)

        return self.client.post(
            self.ENDPOINT,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            },
        )

    @staticmethod
    def _validate(fields):
        if not isinstance(fields, dict):
            raise TypeError("Boundary fields must be a dictionary")

        payload = fields.copy()

        required = (
            "farm_id",
            "farm_updated_cord",
            "farm_calculated_area",
            "farm_calculated_area_unit",
            "boundary_method_type",
        )

        missing = [
            name for name in required
            if payload.get(name) in (None, "")
        ]

        if missing:
            raise ValueError(
                "Boundary request is missing required fields: "
                + ", ".join(missing)
            )

        return payload
