"""
Unit tests for LinkedIn Integration.

Tests cover:
- Helper functions (URN encoding, normalization)
- API client methods
- Action handlers with mocked responses
- Error handling

Run tests: python -m pytest tests/test_linkedin.py -v
"""

import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the integration module
from linkedin import (
    linkedin,
    LinkedInAPIClient,
    encode_urn,
    normalize_person_urn,
    normalize_organization_urn,
    get_rest_headers,
    get_oidc_headers,
    build_base_post_payload,
    get_author_urn,
    GetUserInfoAction,
    ShareContentAction,
    ShareImagePostAction,
    ShareArticlePostAction,
    ShareOrganizationPostAction,
    CreatePollPostAction,
    CreateDraftPostAction,
    GetPostAction,
    GetMemberPostsAction,
    DeletePostAction,
    CreateCommentAction,
    GetPostCommentsAction,
    AddReactionAction,
    LINKEDIN_VERSION,
    LINKEDIN_API_BASE
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_context():
    """Create a mock ExecutionContext for testing."""
    context = MagicMock()
    context.fetch = AsyncMock()
    return context


@pytest.fixture
def mock_user_info():
    """Sample user info response from LinkedIn OIDC."""
    return {
        "sub": "abc123xyz",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "picture": "https://example.com/avatar.jpg",
        "locale": "en_US"
    }


@pytest.fixture
def mock_post_response():
    """Sample post creation response."""
    return {
        "id": "urn:li:share:7123456789012345678"
    }


# =============================================================================
# Test Helper Functions
# =============================================================================

class TestHelperFunctions:
    """Tests for helper/utility functions."""

    def test_encode_urn_basic(self):
        """Test URN encoding for URL paths."""
        urn = "urn:li:share:123456"
        encoded = encode_urn(urn)
        assert ":" not in encoded
        assert encoded == "urn%3Ali%3Ashare%3A123456"

    def test_encode_urn_with_special_chars(self):
        """Test URN encoding with special characters."""
        urn = "urn:li:ugcPost:12345/test"
        encoded = encode_urn(urn)
        assert "/" not in encoded

    def test_normalize_person_urn_with_id(self):
        """Test normalizing a raw person ID to URN."""
        result = normalize_person_urn("abc123")
        assert result == "urn:li:person:abc123"

    def test_normalize_person_urn_already_urn(self):
        """Test normalizing already-formatted URN."""
        urn = "urn:li:person:abc123"
        result = normalize_person_urn(urn)
        assert result == urn

    def test_normalize_person_urn_empty_raises(self):
        """Test that empty value raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            normalize_person_urn("")

    def test_normalize_organization_urn_with_id(self):
        """Test normalizing a raw organization ID to URN."""
        result = normalize_organization_urn("12345")
        assert result == "urn:li:organization:12345"

    def test_normalize_organization_urn_already_urn(self):
        """Test normalizing already-formatted organization URN."""
        urn = "urn:li:organization:12345"
        result = normalize_organization_urn(urn)
        assert result == urn

    def test_get_rest_headers(self):
        """Test REST API headers include required fields."""
        headers = get_rest_headers()
        assert headers["LinkedIn-Version"] == LINKEDIN_VERSION
        assert headers["X-Restli-Protocol-Version"] == "2.0.0"
        assert headers["Content-Type"] == "application/json"

    def test_get_oidc_headers(self):
        """Test OIDC headers don't include LinkedIn-Version."""
        headers = get_oidc_headers()
        assert "LinkedIn-Version" not in headers
        assert headers["Content-Type"] == "application/json"

    def test_build_base_post_payload(self):
        """Test building base post payload."""
        payload = build_base_post_payload(
            author_urn="urn:li:person:123",
            commentary="Hello LinkedIn!",
            visibility="PUBLIC",
            lifecycle_state="PUBLISHED"
        )
        assert payload["author"] == "urn:li:person:123"
        assert payload["commentary"] == "Hello LinkedIn!"
        assert payload["visibility"] == "PUBLIC"
        assert payload["lifecycleState"] == "PUBLISHED"
        # Should NOT have extra fields that could cause API errors
        assert "distribution" not in payload
        assert "isReshareDisabledByAuthor" not in payload

    def test_build_base_post_payload_defaults(self):
        """Test default values in base payload."""
        payload = build_base_post_payload("urn:li:person:123", "Test")
        assert payload["visibility"] == "PUBLIC"
        assert payload["lifecycleState"] == "PUBLISHED"


# =============================================================================
# Test API Client
# =============================================================================

class TestLinkedInAPIClient:
    """Tests for LinkedInAPIClient class."""

    @pytest.mark.asyncio
    async def test_get_current_user(self, mock_context, mock_user_info):
        """Test fetching current user info."""
        mock_context.fetch.return_value = mock_user_info
        client = LinkedInAPIClient(mock_context)

        result = await client.get_current_user()

        assert result["sub"] == "abc123xyz"
        assert result["name"] == "John Doe"
        mock_context.fetch.assert_called_once()
        call_args = mock_context.fetch.call_args
        assert "v2/userinfo" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_create_post(self, mock_context, mock_post_response):
        """Test creating a post."""
        mock_context.fetch.return_value = mock_post_response
        client = LinkedInAPIClient(mock_context)

        payload = {"author": "urn:li:person:123", "commentary": "Test"}
        result = await client.create_post(payload)

        assert result["id"] == "urn:li:share:7123456789012345678"
        mock_context.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_post_encodes_urn(self, mock_context):
        """Test that get_post properly encodes URN in URL."""
        mock_context.fetch.return_value = {"id": "test"}
        client = LinkedInAPIClient(mock_context)

        await client.get_post("urn:li:share:123")

        call_url = mock_context.fetch.call_args[0][0]
        # Should not contain raw colons in path
        assert "urn%3Ali%3Ashare%3A123" in call_url

    @pytest.mark.asyncio
    async def test_delete_post_encodes_urn(self, mock_context):
        """Test that delete_post properly encodes URN in URL."""
        mock_context.fetch.return_value = None
        client = LinkedInAPIClient(mock_context)

        await client.delete_post("urn:li:share:123")

        call_url = mock_context.fetch.call_args[0][0]
        assert "urn%3Ali%3Ashare%3A123" in call_url

    @pytest.mark.asyncio
    async def test_create_comment_encodes_urn(self, mock_context):
        """Test that create_comment properly encodes URN."""
        mock_context.fetch.return_value = {"id": "comment123"}
        client = LinkedInAPIClient(mock_context)

        await client.create_comment(
            "urn:li:share:123",
            "urn:li:person:456",
            "Great post!"
        )

        call_url = mock_context.fetch.call_args[0][0]
        assert "urn%3Ali%3Ashare%3A123" in call_url

    @pytest.mark.asyncio
    async def test_api_error_includes_context(self, mock_context):
        """Test that API errors include endpoint context."""
        mock_context.fetch.side_effect = Exception("Connection failed")
        client = LinkedInAPIClient(mock_context)

        with pytest.raises(Exception) as exc_info:
            await client.create_post({"test": "data"})

        assert "LinkedIn API error" in str(exc_info.value)
        assert "rest/posts" in str(exc_info.value)


# =============================================================================
# Test get_author_urn Helper
# =============================================================================

class TestGetAuthorUrn:
    """Tests for get_author_urn function."""

    @pytest.mark.asyncio
    async def test_with_provided_id(self, mock_context):
        """Test with explicitly provided author ID."""
        result = await get_author_urn(mock_context, "myid123")
        assert result == "urn:li:person:myid123"
        # Should not make API call when ID provided
        mock_context.fetch.assert_not_called()

    @pytest.mark.asyncio
    async def test_with_provided_urn(self, mock_context):
        """Test with already-formatted URN."""
        result = await get_author_urn(mock_context, "urn:li:person:myid123")
        assert result == "urn:li:person:myid123"

    @pytest.mark.asyncio
    async def test_fetches_user_when_not_provided(self, mock_context, mock_user_info):
        """Test that it fetches user info when ID not provided."""
        mock_context.fetch.return_value = mock_user_info

        result = await get_author_urn(mock_context, None)

        assert result == "urn:li:person:abc123xyz"
        mock_context.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self, mock_context):
        """Test error when user info doesn't contain ID."""
        mock_context.fetch.return_value = {}

        with pytest.raises(Exception, match="Could not determine current user ID"):
            await get_author_urn(mock_context, None)


# =============================================================================
# Test Action Handlers
# =============================================================================

class TestGetUserInfoAction:
    """Tests for GetUserInfoAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context, mock_user_info):
        """Test successful user info retrieval."""
        mock_context.fetch.return_value = mock_user_info
        action = GetUserInfoAction()

        result = await action.execute({}, mock_context)

        assert result.data["result"] is True
        assert result.data["user_id"] == "abc123xyz"
        assert result.data["name"] == "John Doe"
        assert result.cost_usd == 0.0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_context):
        """Test error handling."""
        mock_context.fetch.side_effect = Exception("Network error")
        action = GetUserInfoAction()

        result = await action.execute({}, mock_context)

        assert result.data["result"] is False
        assert "error" in result.data


class TestShareContentAction:
    """Tests for ShareContentAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context, mock_user_info, mock_post_response):
        """Test successful text post creation."""
        # First call for user info, second for post creation
        mock_context.fetch.side_effect = [mock_user_info, mock_post_response]
        action = ShareContentAction()

        result = await action.execute({"content": "Hello LinkedIn!"}, mock_context)

        assert result.data["result"] is True
        assert "post_id" in result.data

    @pytest.mark.asyncio
    async def test_missing_content_fails(self, mock_context):
        """Test that missing content raises error."""
        action = ShareContentAction()

        result = await action.execute({}, mock_context)

        assert result.data["result"] is False
        assert "Content is required" in result.data["error"]

    @pytest.mark.asyncio
    async def test_with_explicit_author_id(self, mock_context, mock_post_response):
        """Test with explicit author ID (no user fetch needed)."""
        mock_context.fetch.return_value = mock_post_response
        action = ShareContentAction()

        result = await action.execute({
            "content": "Test post",
            "author_id": "explicit123"
        }, mock_context)

        assert result.data["result"] is True
        # Only one API call (post creation), not user fetch
        assert mock_context.fetch.call_count == 1


class TestShareArticlePostAction:
    """Tests for ShareArticlePostAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context, mock_user_info, mock_post_response):
        """Test successful article post creation."""
        mock_context.fetch.side_effect = [mock_user_info, mock_post_response]
        action = ShareArticlePostAction()

        result = await action.execute({
            "content": "Check out this article!",
            "article_url": "https://example.com/article",
            "article_title": "Great Article"
        }, mock_context)

        assert result.data["result"] is True

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, mock_context):
        """Test that missing URL/title fails."""
        action = ShareArticlePostAction()

        result = await action.execute({
            "content": "Test",
            "article_url": "https://example.com"
            # Missing article_title
        }, mock_context)

        assert result.data["result"] is False
        assert "required" in result.data["error"]


class TestShareOrganizationPostAction:
    """Tests for ShareOrganizationPostAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context, mock_post_response):
        """Test successful organization post."""
        mock_context.fetch.return_value = mock_post_response
        action = ShareOrganizationPostAction()

        result = await action.execute({
            "content": "Company update!",
            "organization_id": "12345"
        }, mock_context)

        assert result.data["result"] is True

    @pytest.mark.asyncio
    async def test_accepts_full_urn(self, mock_context, mock_post_response):
        """Test that full organization URN is accepted."""
        mock_context.fetch.return_value = mock_post_response
        action = ShareOrganizationPostAction()

        result = await action.execute({
            "content": "Company update!",
            "organization_id": "urn:li:organization:12345"
        }, mock_context)

        assert result.data["result"] is True


class TestCreatePollPostAction:
    """Tests for CreatePollPostAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context, mock_user_info, mock_post_response):
        """Test successful poll creation."""
        mock_context.fetch.side_effect = [mock_user_info, mock_post_response]
        action = CreatePollPostAction()

        result = await action.execute({
            "content": "What's your favorite color?",
            "options": ["Red", "Blue", "Green"]
        }, mock_context)

        assert result.data["result"] is True

    @pytest.mark.asyncio
    async def test_too_few_options_fails(self, mock_context):
        """Test that fewer than 2 options fails."""
        action = CreatePollPostAction()

        result = await action.execute({
            "content": "Poll",
            "options": ["Only one"]
        }, mock_context)

        assert result.data["result"] is False
        assert "2-4 options" in result.data["error"]

    @pytest.mark.asyncio
    async def test_too_many_options_fails(self, mock_context):
        """Test that more than 4 options fails."""
        action = CreatePollPostAction()

        result = await action.execute({
            "content": "Poll",
            "options": ["A", "B", "C", "D", "E"]
        }, mock_context)

        assert result.data["result"] is False
        assert "2-4 options" in result.data["error"]


class TestCreateDraftPostAction:
    """Tests for CreateDraftPostAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context, mock_user_info, mock_post_response):
        """Test successful draft creation."""
        mock_context.fetch.side_effect = [mock_user_info, mock_post_response]
        action = CreateDraftPostAction()

        result = await action.execute({
            "content": "Draft content"
        }, mock_context)

        assert result.data["result"] is True
        assert result.data["status"] == "DRAFT"


class TestAddReactionAction:
    """Tests for AddReactionAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context, mock_user_info):
        """Test successful reaction."""
        mock_context.fetch.side_effect = [mock_user_info, {}]
        action = AddReactionAction()

        result = await action.execute({
            "post_urn": "urn:li:share:123",
            "reaction_type": "LIKE"
        }, mock_context)

        assert result.data["result"] is True
        assert result.data["reaction_type"] == "LIKE"

    @pytest.mark.asyncio
    async def test_invalid_reaction_type(self, mock_context):
        """Test that invalid reaction type fails."""
        action = AddReactionAction()

        result = await action.execute({
            "post_urn": "urn:li:share:123",
            "reaction_type": "INVALID"
        }, mock_context)

        assert result.data["result"] is False
        assert "Invalid reaction_type" in result.data["error"]

    @pytest.mark.asyncio
    async def test_all_valid_reaction_types(self, mock_context, mock_user_info):
        """Test all valid reaction types are accepted."""
        valid_types = ["LIKE", "PRAISE", "APPRECIATION", "EMPATHY", "INTEREST", "ENTERTAINMENT"]

        for reaction in valid_types:
            mock_context.fetch.reset_mock()
            mock_context.fetch.side_effect = [mock_user_info, {}]
            action = AddReactionAction()

            result = await action.execute({
                "post_urn": "urn:li:share:123",
                "reaction_type": reaction
            }, mock_context)

            assert result.data["result"] is True, f"Failed for reaction: {reaction}"


class TestDeletePostAction:
    """Tests for DeletePostAction."""

    @pytest.mark.asyncio
    async def test_success(self, mock_context):
        """Test successful post deletion."""
        mock_context.fetch.return_value = None
        action = DeletePostAction()

        result = await action.execute({
            "post_urn": "urn:li:share:123"
        }, mock_context)

        assert result.data["result"] is True
        assert result.data["deleted_post_urn"] == "urn:li:share:123"

    @pytest.mark.asyncio
    async def test_missing_urn_fails(self, mock_context):
        """Test that missing post_urn fails."""
        action = DeletePostAction()

        result = await action.execute({}, mock_context)

        assert result.data["result"] is False
        assert "required" in result.data["error"]


# =============================================================================
# Test Error Scenarios
# =============================================================================

class TestErrorScenarios:
    """Tests for various error scenarios."""

    @pytest.mark.asyncio
    async def test_network_error_handling(self, mock_context):
        """Test that network errors are properly caught."""
        mock_context.fetch.side_effect = Exception("Connection timeout")
        action = GetUserInfoAction()

        result = await action.execute({}, mock_context)

        assert result.data["result"] is False
        assert "error" in result.data
        assert result.cost_usd == 0.0

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context):
        """Test handling of API error responses."""
        mock_context.fetch.side_effect = Exception("401 Unauthorized")
        action = ShareContentAction()

        result = await action.execute({"content": "Test"}, mock_context)

        assert result.data["result"] is False


# =============================================================================
# Integration Smoke Tests (require real credentials)
# =============================================================================

class TestIntegrationSmoke:
    """
    Smoke tests for integration. These require real credentials.
    Skip in CI by checking for environment variables.
    """

    @pytest.fixture
    def real_context(self):
        """Create a real context with credentials from environment."""
        import os
        token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
        if not token:
            pytest.skip("LINKEDIN_ACCESS_TOKEN not set")
        
        # This would need the actual SDK implementation
        # For now, skip these tests
        pytest.skip("Integration tests require SDK setup")

    @pytest.mark.asyncio
    async def test_real_get_user_info(self, real_context):
        """Test real API call to get user info."""
        action = GetUserInfoAction()
        result = await action.execute({}, real_context)
        assert result.data["result"] is True


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    print("Running LinkedIn Integration Tests")
    print("=" * 50)
    pytest.main([__file__, "-v", "--tb=short"])
