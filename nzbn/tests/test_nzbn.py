import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.auth = {
        "credentials": {
            "subscription_key": "test-subscription-key",
            "environment": "sandbox"
        }
    }
    context.fetch = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_search_entities_success(mock_context):
    from nzbn import SearchEntitiesAction
    
    mock_context.fetch.return_value = {
        "pageSize": 10,
        "page": 0,
        "totalItems": 2,
        "items": [
            {
                "nzbn": "9429000106078",
                "entityName": "Test Company Ltd",
                "entityTypeCode": "LTD",
                "entityTypeDescription": "NZ Limited Company",
                "entityStatusCode": "50",
                "entityStatusDescription": "Registered",
                "registrationDate": "2020-01-15T00:00:00",
                "tradingNames": [
                    {"name": "Test Trading", "startDate": "2020-01-15T00:00:00", "endDate": None}
                ],
                "classifications": [
                    {"classificationCode": "A011100", "classificationDescription": "Nursery Production"}
                ]
            }
        ]
    }
    
    action = SearchEntitiesAction()
    result = await action.execute({"search_term": "Test Company"}, mock_context)
    
    assert result["total_items"] == 2
    assert len(result["items"]) == 1
    assert result["items"][0]["nzbn"] == "9429000106078"
    assert result["items"][0]["entity_name"] == "Test Company Ltd"


@pytest.mark.asyncio
async def test_search_entities_with_filters(mock_context):
    from nzbn import SearchEntitiesAction
    
    mock_context.fetch.return_value = {"pageSize": 5, "page": 0, "totalItems": 0, "items": []}
    
    action = SearchEntitiesAction()
    await action.execute({
        "search_term": "Test",
        "entity_status": "Registered",
        "entity_type": "NZCompany",
        "page": 0,
        "page_size": 5
    }, mock_context)
    
    call_args = mock_context.fetch.call_args
    params = call_args.kwargs["params"]
    assert params["search-term"] == "Test"
    assert params["entity-status"] == "Registered"
    assert params["entity-type"] == "NZCompany"


@pytest.mark.asyncio
async def test_get_entity_success(mock_context):
    from nzbn import GetEntityAction
    
    mock_context.fetch.return_value = {
        "nzbn": "9429000106078",
        "entityName": "Test Company Ltd",
        "entityTypeCode": "LTD",
        "entityStatusCode": "50",
        "addresses": [
            {"addressType": "RegisteredOffice", "address1": "123 Test St", "city": "Auckland", "postCode": "1010"}
        ],
        "roles": [
            {"roleType": "Director", "roleStatus": "Active", "rolePerson": {"firstName": "John", "lastName": "Smith"}}
        ]
    }
    
    action = GetEntityAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert result["nzbn"] == "9429000106078"
    assert result["entity_name"] == "Test Company Ltd"
    assert len(result["addresses"]) == 1
    assert len(result["roles"]) == 1
    assert result["roles"][0]["person_name"] == "John Smith"


@pytest.mark.asyncio
async def test_get_entity_invalid_nzbn(mock_context):
    from nzbn import GetEntityAction
    
    action = GetEntityAction()
    with pytest.raises(ValueError, match="NZBN must be a 13-digit number"):
        await action.execute({"nzbn": "12345"}, mock_context)


@pytest.mark.asyncio
async def test_get_entity_changes_success(mock_context):
    from nzbn import GetEntityChangesAction
    
    mock_context.fetch.return_value = {
        "totalItems": 5,
        "page": 0,
        "pageSize": 10,
        "items": [
            {"nzbn": "9429000106078", "entityName": "Test Company", "changeEventType": "DirectorChanged"}
        ]
    }
    
    action = GetEntityChangesAction()
    result = await action.execute({"change_event_type": "DirectorChanged"}, mock_context)
    
    assert result["total_items"] == 5
    assert len(result["items"]) == 1


@pytest.mark.asyncio
async def test_get_entity_roles_success(mock_context):
    from nzbn import GetEntityRolesAction
    
    mock_context.fetch.return_value = {
        "items": [
            {"roleType": "Director", "roleStatus": "Active", "rolePerson": {"firstName": "Jane", "lastName": "Doe"}},
            {"roleType": "Shareholder", "roleStatus": "Active", "roleEntity": {"entityName": "Holding Co", "nzbn": "9429000123456"}}
        ]
    }
    
    action = GetEntityRolesAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert result["nzbn"] == "9429000106078"
    assert len(result["roles"]) == 2
    assert result["roles"][0]["person_name"] == "Jane Doe"
    assert result["roles"][1]["entity_name"] == "Holding Co"


@pytest.mark.asyncio
async def test_get_entity_addresses_success(mock_context):
    from nzbn import GetEntityAddressesAction
    
    mock_context.fetch.return_value = {
        "items": [
            {"addressType": "RegisteredOffice", "address1": "Level 10", "address2": "100 Queen St", "city": "Auckland", "postCode": "1010"},
            {"addressType": "PostalAddress", "address1": "PO Box 1234", "city": "Auckland", "postCode": "1140"}
        ]
    }
    
    action = GetEntityAddressesAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert result["nzbn"] == "9429000106078"
    assert len(result["addresses"]) == 2
    assert result["addresses"][0]["address_type"] == "RegisteredOffice"


@pytest.mark.asyncio
async def test_get_entity_trading_names_success(mock_context):
    from nzbn import GetEntityTradingNamesAction
    
    mock_context.fetch.return_value = {
        "items": [
            {"name": "Trading Name 1", "startDate": "2020-01-01T00:00:00"},
            {"name": "Trading Name 2", "startDate": "2021-06-15T00:00:00"}
        ]
    }
    
    action = GetEntityTradingNamesAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert len(result["trading_names"]) == 2
    assert result["trading_names"][0]["name"] == "Trading Name 1"


@pytest.mark.asyncio
async def test_get_entity_phone_numbers_success(mock_context):
    from nzbn import GetEntityPhoneNumbersAction
    
    mock_context.fetch.return_value = {
        "items": [{"phoneType": "Business", "phoneCountryCode": "64", "phoneAreaCode": "9", "phoneNumber": "1234567"}]
    }
    
    action = GetEntityPhoneNumbersAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert len(result["phone_numbers"]) == 1
    assert result["phone_numbers"][0]["phone_number"] == "1234567"


@pytest.mark.asyncio
async def test_get_entity_email_addresses_success(mock_context):
    from nzbn import GetEntityEmailAddressesAction
    
    mock_context.fetch.return_value = {
        "items": [{"emailAddressType": "Business", "emailAddress": "info@test.co.nz"}]
    }
    
    action = GetEntityEmailAddressesAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert len(result["email_addresses"]) == 1
    assert result["email_addresses"][0]["email"] == "info@test.co.nz"


@pytest.mark.asyncio
async def test_get_entity_websites_success(mock_context):
    from nzbn import GetEntityWebsitesAction
    
    mock_context.fetch.return_value = {
        "items": [{"url": "https://www.test.co.nz", "websiteType": "Business"}]
    }
    
    action = GetEntityWebsitesAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert len(result["websites"]) == 1
    assert result["websites"][0]["url"] == "https://www.test.co.nz"


@pytest.mark.asyncio
async def test_get_entity_gst_numbers_success(mock_context):
    from nzbn import GetEntityGstNumbersAction
    
    mock_context.fetch.return_value = {
        "items": [{"gstNumber": "123-456-789", "startDate": "2020-01-01T00:00:00"}]
    }
    
    action = GetEntityGstNumbersAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert len(result["gst_numbers"]) == 1
    assert result["gst_numbers"][0]["gst_number"] == "123-456-789"


@pytest.mark.asyncio
async def test_get_entity_industry_classifications_success(mock_context):
    from nzbn import GetEntityIndustryClassificationsAction
    
    mock_context.fetch.return_value = {
        "items": [{"classificationCode": "L672000", "classificationDescription": "Property Operators"}]
    }
    
    action = GetEntityIndustryClassificationsAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert len(result["classifications"]) == 1
    assert result["classifications"][0]["code"] == "L672000"


@pytest.mark.asyncio
async def test_get_entity_company_details_success(mock_context):
    from nzbn import GetEntityCompanyDetailsAction
    
    mock_context.fetch.return_value = {
        "constitutionFiled": True,
        "annualReturnFilingMonth": 3,
        "annualReturnLastFiledDate": "2024-03-15T00:00:00"
    }
    
    action = GetEntityCompanyDetailsAction()
    result = await action.execute({"nzbn": "9429000106078"}, mock_context)
    
    assert result["company_details"]["constitution_filed"] is True
    assert result["company_details"]["annual_return_filing_month"] == 3


@pytest.mark.asyncio
async def test_sandbox_environment(mock_context):
    from nzbn import get_base_url, SANDBOX_BASE_URL
    
    mock_context.auth = {"credentials": {"subscription_key": "key", "environment": "sandbox"}}
    assert get_base_url(mock_context) == SANDBOX_BASE_URL


@pytest.mark.asyncio
async def test_production_environment(mock_context):
    from nzbn import get_base_url, PRODUCTION_BASE_URL
    
    mock_context.auth = {"credentials": {"subscription_key": "key", "environment": "production"}}
    assert get_base_url(mock_context) == PRODUCTION_BASE_URL


@pytest.mark.asyncio
async def test_api_error_response(mock_context):
    from nzbn import SearchEntitiesAction
    
    mock_context.fetch.return_value = {"errorCode": "401", "errorDescription": "Permission Denied"}
    
    action = SearchEntitiesAction()
    with pytest.raises(Exception, match="Permission Denied"):
        await action.execute({"search_term": "Test"}, mock_context)
