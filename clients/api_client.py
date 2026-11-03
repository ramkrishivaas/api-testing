import requests
from config import settings 

class APIClient:
    """Shared requests session. Requests builds multipart boundaries automatically."""

    def __init__(self, base_url=None, token=None, timeout=None):
        self.base_url = (base_url or settings.API_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "*/*",
            "Authorization": f"Bearer {token or settings.API_TOKEN}" if (token or settings.API_TOKEN) else "",
        })
        # Remove empty Authorization header rather than sending "Bearer ".
        if not self.session.headers.get("Authorization"):
            self.session.headers.pop("Authorization", None)

    def request(self, method, path, *, data=None, json=None, files=None, headers=None):
        url = path if path.startswith(("http://", "https://")) else f"{self.base_url}/{path.lstrip('/')}"
        request_headers = dict(headers or {})
        # Do not set Content-Type for multipart forms: requests must generate its boundary.
        response = self.session.request(
            method=method.upper(),
            url=url,
            data=data,
            json=json,
            files=files,
            headers=request_headers,
            timeout=self.timeout,
            verify=settings.VERIFY_TLS,
        )
        return response

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def close(self):
        self.session.close()
