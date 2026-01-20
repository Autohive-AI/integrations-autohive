import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from linkedin_ads import (
    extract_id_from_urn,
    build_urn,
    get_headers,
    API_VERSION
)


class TestHelperFunctions:
    def test_extract_id_from_urn(self):
        assert extract_id_from_urn("urn:li:sponsoredAccount:123456789") == "123456789"
        assert extract_id_from_urn("urn:li:sponsoredCampaign:987654321") == "987654321"
        assert extract_id_from_urn("123456789") == "123456789"
        assert extract_id_from_urn("") == ""

    def test_build_urn(self):
        assert build_urn("account", "123456789") == "urn:li:sponsoredAccount:123456789"
        assert build_urn("campaign", "987654321") == "urn:li:sponsoredCampaign:987654321"
        assert build_urn("campaign_group", "111222333") == "urn:li:sponsoredCampaignGroup:111222333"
        assert build_urn("account", "urn:li:sponsoredAccount:123456789") == "urn:li:sponsoredAccount:123456789"

    def test_get_headers(self):
        headers = get_headers()
        assert headers["Authorization"].startswith("Bearer ")
        assert headers["LinkedIn-Version"] == API_VERSION
        assert headers["X-Restli-Protocol-Version"] == "2.0.0"
        assert headers["Content-Type"] == "application/json"
