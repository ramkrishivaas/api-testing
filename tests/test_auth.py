import pytest
from config import settings

@pytest.mark.integration
def test_token_is_configured():
    assert settings.API_TOKEN, "Set API_TOKEN in .env before running staging API tests."
