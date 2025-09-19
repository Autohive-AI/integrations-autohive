# Test for Xero Accounting integration
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from context import xero
from autohive_integrations_sdk import ExecutionContext
from xero import XeroRateLimiter, XeroRateLimitExceededException

async def test_get_available_connections():
    """
    Test the get_available_connections action
    """
    # Import xero integration lazily to avoid config issues during module import
    from context import xero
    
    # Setup mock auth object (platform auth for Xero)
    auth = {}  # Platform auth tokens are handled automatically by ExecutionContext

    inputs = {}  # No inputs required for get_available_connections

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await xero.execute_action("get_available_connections", inputs, context)
            print(f"Success: Retrieved {len(result.get('companies', []))} available connections")
            if result.get('companies'):
                for company in result['companies']:
                    print(f"  - ID: {company.get('tenant_id')}, Name: {company.get('company_name')}")
            return result
        except Exception as e:
            print(f"Error testing get_available_connections: {str(e)}")
            return None

async def test_get_aged_payables_with_specific_tenant():
    """
    Test fetching aged payables with a specific tenant ID
    """
    # First get available connections
    connections_result = await test_get_available_connections()
    if not connections_result or not connections_result.get('companies'):
        print("Cannot test aged payables without tenant information")
        return

    # Use the first available tenant
    tenant_id = connections_result['companies'][0]['tenant_id']
    print(f"Using tenant ID: {tenant_id}")

    auth = {}
    inputs = {
        "tenant_id": tenant_id,
        "contact_id": "test-contact-id-123"  # Replace with actual contact ID
    }

    async with ExecutionContext(auth=auth) as context:
        try:
            result = await xero.execute_action("get_aged_payables", inputs, context)
            print(f"Success: Retrieved aged payables report")
            return result
        except Exception as e:
            print(f"Error testing aged payables: {str(e)}")
            return None

async def main():
    print("Testing Xero Integration")
    print("==================================")
    
    print("\n1. Testing get_available_connections...")
    await test_get_available_connections()
    
    print("\n2. Testing aged payables with tenant ID...")
    await test_get_aged_payables_with_specific_tenant()
    
    print("\n3. Running rate limiting tests...")
    print("To run rate limiting tests, use: pytest tests/test_xero.py -v")

# ---- Rate Limiting Tests ----

class MockResponse:
    """Mock response object for testing"""
    def __init__(self, headers=None):
        self.headers = headers or {}


class MockRateLimitError(Exception):
    """Mock exception that simulates a 429 rate limit error"""
    def __init__(self, message="429 Rate limit exceeded", headers=None):
        super().__init__(message)
        self.headers = headers or {}


@pytest.mark.asyncio
async def test_rate_limiter_successful_request():
    """Test that successful requests work normally"""
    limiter = XeroRateLimiter()
    context = Mock()
    context.fetch = AsyncMock(return_value={"success": True})
    
    result = await limiter.make_request(
        context, 
        "https://api.xero.com/test", 
        "tenant-123",
        method="GET"
    )
    
    assert result == {"success": True}
    context.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limiter_short_delay_retry():
    """Test that short rate limit delays result in retry and success"""
    limiter = XeroRateLimiter(max_wait_time=60, default_retry_delay=10)
    context = Mock()
    
    # First call raises rate limit, second succeeds
    rate_limit_error = MockRateLimitError(
        "429 Too Many Requests",
        headers={"Retry-After": "5"}
    )
    context.fetch = AsyncMock(side_effect=[rate_limit_error, {"success": True}])
    
    with patch('asyncio.sleep') as mock_sleep:
        result = await limiter.make_request(
            context,
            "https://api.xero.com/test",
            "tenant-123",
            method="GET"
        )
    
    assert result == {"success": True}
    assert context.fetch.call_count == 2
    mock_sleep.assert_called_once_with(5)


@pytest.mark.asyncio
async def test_rate_limiter_long_delay_exception():
    """Test that long rate limit delays raise XeroRateLimitExceededException"""
    limiter = XeroRateLimiter(max_wait_time=60, default_retry_delay=10)
    context = Mock()
    
    rate_limit_error = MockRateLimitError(
        "429 Too Many Requests",
        headers={"Retry-After": "120"}  # Exceeds max_wait_time of 60
    )
    context.fetch = AsyncMock(side_effect=rate_limit_error)
    
    with pytest.raises(XeroRateLimitExceededException) as exc_info:
        await limiter.make_request(
            context,
            "https://api.xero.com/test",
            "tenant-123",
            method="GET"
        )
    
    exception = exc_info.value
    assert exception.requested_delay == 120
    assert exception.max_wait_time == 60
    assert exception.tenant_id == "tenant-123"
    assert "exceeds maximum wait time" in str(exception)


@pytest.mark.asyncio
async def test_rate_limiter_exhausted_retries():
    """Test that exhausted retries raise the last error"""
    limiter = XeroRateLimiter(max_retries=2, max_wait_time=60, default_retry_delay=10)
    context = Mock()
    
    rate_limit_error = MockRateLimitError(
        "429 Too Many Requests",
        headers={"Retry-After": "5"}
    )
    context.fetch = AsyncMock(side_effect=rate_limit_error)
    
    with patch('asyncio.sleep'):
        with pytest.raises(MockRateLimitError):
            await limiter.make_request(
                context,
                "https://api.xero.com/test",
                "tenant-123",
                method="GET"
            )
    
    # Should call fetch max_retries + 1 times (initial + retries)
    assert context.fetch.call_count == 3


@pytest.mark.asyncio
async def test_rate_limiter_non_rate_limit_error():
    """Test that non-rate-limit errors are raised immediately without retries"""
    limiter = XeroRateLimiter()
    context = Mock()
    
    other_error = Exception("500 Internal Server Error")
    context.fetch = AsyncMock(side_effect=other_error)
    
    with pytest.raises(Exception) as exc_info:
        await limiter.make_request(
            context,
            "https://api.xero.com/test",
            "tenant-123",
            method="GET"
        )
    
    assert str(exc_info.value) == "500 Internal Server Error"
    context.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limiter_default_delay_no_header():
    """Test that default delay is used when Retry-After header is missing"""
    limiter = XeroRateLimiter(default_retry_delay=30, max_wait_time=60)
    context = Mock()
    
    # Rate limit error without Retry-After header
    rate_limit_error = MockRateLimitError("429 Too Many Requests")
    context.fetch = AsyncMock(side_effect=[rate_limit_error, {"success": True}])
    
    with patch('asyncio.sleep') as mock_sleep:
        result = await limiter.make_request(
            context,
            "https://api.xero.com/test",
            "tenant-123",
            method="GET"
        )
    
    assert result == {"success": True}
    mock_sleep.assert_called_once_with(30)  # Should use default_retry_delay


@pytest.mark.asyncio
async def test_rate_limiter_invalid_retry_after_header():
    """Test that invalid Retry-After header falls back to default delay"""
    limiter = XeroRateLimiter(default_retry_delay=25, max_wait_time=60)
    context = Mock()
    
    rate_limit_error = MockRateLimitError(
        "429 Too Many Requests",
        headers={"Retry-After": "invalid-value"}
    )
    context.fetch = AsyncMock(side_effect=[rate_limit_error, {"success": True}])
    
    with patch('asyncio.sleep') as mock_sleep:
        result = await limiter.make_request(
            context,
            "https://api.xero.com/test",
            "tenant-123",
            method="GET"
        )
    
    assert result == {"success": True}
    mock_sleep.assert_called_once_with(25)  # Should use default_retry_delay


@pytest.mark.asyncio
async def test_rate_limiter_tenant_header_added():
    """Test that xero-tenant-id header is properly added to requests"""
    limiter = XeroRateLimiter()
    context = Mock()
    context.fetch = AsyncMock(return_value={"success": True})
    
    await limiter.make_request(
        context,
        "https://api.xero.com/test",
        "tenant-123",
        method="GET",
        headers={"Accept": "application/json"}
    )
    
    # Verify the call was made with tenant header added
    context.fetch.assert_called_once_with(
        "https://api.xero.com/test",
        method="GET",
        headers={
            "Accept": "application/json",
            "xero-tenant-id": "tenant-123"
        }
    )


@pytest.mark.asyncio
async def test_find_contact_rate_limit_exception_handling():
    """Test that action handlers properly handle XeroRateLimitExceededException"""
    # Import xero integration lazily to avoid config issues during module import
    from context import xero
    
    auth = {}
    inputs = {
        "tenant_id": "test-tenant",
        "contact_name": "Test Contact"
    }
    
    # Mock the rate limiter to raise XeroRateLimitExceededException
    with patch('xero.rate_limiter') as mock_limiter:
        mock_limiter.make_request = AsyncMock(
            side_effect=XeroRateLimitExceededException(
                requested_delay=120,
                max_wait_time=60,
                tenant_id="test-tenant"
            )
        )
        
        async with ExecutionContext(auth=auth) as context:
            result = await xero.execute_action("find_contact_by_name", inputs, context)
            
            assert result["success"] is False
            assert result["error_type"] == "rate_limit_exceeded"
            assert result["tenant_id"] == "test-tenant"
            assert result["retry_delay_seconds"] == 120
            assert "exceeds maximum" in result["message"]


if __name__ == "__main__":
    asyncio.run(main())
