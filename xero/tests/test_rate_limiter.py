# Isolated tests for XeroRateLimiter without integration dependencies
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch


class XeroRateLimitExceededException(Exception):
    """
    Exception raised when Xero API rate limit wait time exceeds maximum threshold.
    Provides structured info for LLM.
    """
    def __init__(self, requested_delay: int, max_wait_time: int, tenant_id: str):
        self.requested_delay = requested_delay
        self.max_wait_time = max_wait_time
        self.tenant_id = tenant_id
        
        super().__init__(
            f"Xero API rate limit for tenant {tenant_id} requires waiting {requested_delay}s, "
            f"exceeds maximum wait time of {max_wait_time}s"
        )


class XeroRateLimiter:
    def __init__(self, default_retry_delay: int = 60, max_retries: int = 3, max_wait_time: int = 60):
        """
        Handles Xero API rate limiting by retrying requests on 429 errors.
        Prevents lambda from waiting too long by setting maximum wait time.
        """
        self.default_retry_delay = default_retry_delay
        self.max_retries = max_retries
        self.max_wait_time = max_wait_time
    
    def _extract_retry_delay(self, error_response) -> int:
        """Extract retry delay from error response headers"""
        if hasattr(error_response, 'headers'):
            retry_after = error_response.headers.get('Retry-After')
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass
        return self.default_retry_delay
    
    async def make_request(self, context, url: str, tenant_id: str, **kwargs):
        """Make request to Xero API with automatic retry on rate limit errors"""
        # Add tenant header to the request
        headers = kwargs.get('headers', {})
        headers['xero-tenant-id'] = tenant_id
        kwargs['headers'] = headers
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await context.fetch(url, **kwargs)
                return response
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a rate limit error (HTTP 429)
                if '429' in error_str or 'rate limit' in error_str or 'too many requests' in error_str:
                    # Don't retry on the last attempt
                    if attempt >= self.max_retries:
                        break
                        
                    # Get delay from response headers or use default
                    delay = self._extract_retry_delay(e)
                    
                    # Check if delay exceeds maximum wait time
                    if delay > self.max_wait_time:
                        # Don't wait - inform LLM about rate limit immediately
                        raise XeroRateLimitExceededException(delay, self.max_wait_time, tenant_id)
                    
                    # Short delay - proceed with waiting and retry
                    await asyncio.sleep(delay)
                    continue
                
                # For non-rate-limit errors, fail immediately
                raise e
        
        # All retries exhausted, raise the last error
        raise last_error


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